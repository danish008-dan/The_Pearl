# ============================================
# app.py
# PURPOSE:
# This is the main backend file of the project.
# It handles:
# - Frontend page routes
# - REST APIs
# - Database operations
# - Admin dashboard routes
# ============================================

import os
from dotenv import load_dotenv

from ai.ai_short_description import generate_short_description
from flask import Flask, render_template, jsonify, request, session, redirect
from pycparser.ply.yacc import resultlimit
from werkzeug.security import generate_password_hash, check_password_hash
from ai.nlp_search_gemini import ai_menu_search
from db import get_db_connection

# Load environment variables
load_dotenv()

# Create Flask app (ONLY ONCE)
app = Flask(__name__)

# Set secret key AFTER app creation
app.secret_key = os.getenv("SECRET_KEY")

# ============================================
# DATABASE INITIALIZATION
# PURPOSE:
# Create required tables if they do not exist
# ============================================

def init_db():
    # Open database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            booking_date DATE NOT NULL,
            booking_time TIME NOT NULL,
            guests INT NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# ============================================
# FRONTEND ROUTES
# PURPOSE:
# These routes render HTML pages
# ============================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("menu.html", menu=menu_items)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

def admin_only():
    return "user_id" in session and session.get("role") == "admin"

@app.route("/api/cart")
def get_cart():
    return jsonify(session.get("cart", {}))

@app.route("/cart")
def cart_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("cart.html")

@app.route("/api/cart/clear", methods=["POST"])
def clear_cart():
    session.pop("cart", None)
    return jsonify({"status": "cleared"})


# ============================================
# API ROUTES
# PURPOSE:
# Backend JSON APIs
# ============================================

# Health check API
@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Flask backend running"
    })


# --------------------------------------------
# MENU API (GET)
# PURPOSE:
# Fetch menu items from database
# --------------------------------------------
@app.route("/api/menu")
def get_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(menu_items)


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, hashed_password, "user")
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Username already exists"
        }), 400


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        return jsonify({
            "status": "success",
            "role": user["role"]
        })

    return jsonify({
        "status": "error",
        "message": "Invalid credentials"
    }), 401

# --------------------------------------------
# BOOK TABLE API (POST)
# PURPOSE:
# Save booking details into database
# --------------------------------------------
@app.route("/api/book-table", methods=["POST"])
def book_table():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO bookings (name, phone, booking_date, booking_time, guests)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        data["name"],
        data["phone"],
        data["date"],
        data["time"],
        data["guests"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Booking confirmed"
    })




# ============================================
# USER REGISTRATION
# PURPOSE:
# Allow new users to create account
# ============================================

# PURPOSE:
# Handles user registration

from werkzeug.security import generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, hashed_password, "user")
        )

        conn.commit()
        cursor.close()
        conn.close()

        return "User Registered Successfully"

    return render_template("register.html")


# ============================================
# LOGIN SYSTEM
# PURPOSE:
# Login both admin and users
# ============================================

# PURPOSE:
# Handles user login
from flask import redirect
from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    PURPOSE:
    - Handle login from modal (JSON)
    - Handle login from form (HTML)
    - Use MySQL users table (NO SQLAlchemy)
    """

    if request.method == "POST":

        # ---------- READ INPUT ----------
        if request.is_json:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
        else:
            username = request.form.get("username")
            password = request.form.get("password")

        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Username or password missing"
            }), 400

        # ---------- DB QUERY ----------
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        # ---------- PASSWORD CHECK ----------
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return jsonify({
                "success": True,
                "role": user["role"]
            })

        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401

    # GET request
    return render_template("login.html")



@app.route("/admin/bookings")
def admin_bookings():
    if not admin_only():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM bookings ORDER BY booking_date DESC")
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_bookings.html", bookings=bookings)


@app.route("/admin/users")
def admin_users():
    if not admin_only():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_users.html", users=users)

@app.route("/admin/menu")
def admin_menu():
    if not admin_only():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_menu.html", menu=menu)


@app.route("/admin/menu/add", methods=["POST"])
def add_menu_item():
    if not admin_only():
        return redirect("/login")

    name = request.form["name"]
    description = request.form["description"]
    price = request.form["price"]
    image = request.form["image"]
    category = request.form["category"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO menu (name, description, price, image, category) VALUES (%s,%s,%s,%s,%s)",
        (name, description, price, image, category)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/menu")

@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.json
    item_id = str(data["item_id"])
    price = float(data["price"])

    cart = session.get("cart", {})

    if item_id in cart:
        cart[item_id]["qty"] += 1
    else:
        cart[item_id] = {
            "qty": 1,
            "price": price
        }

    session["cart"] = cart
    session.modified = True

    return jsonify({"status": "added", "cart": cart})


@app.route("/api/order/confirm", methods=["POST"])
def confirm_order():
    if "user_id" not in session or "cart" not in session:
        return jsonify({"error": "No cart"}), 400

    cart = session["cart"]
    total = sum(v["qty"] * v["price"] for v in cart.values())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)",
        (session["user_id"], total)
    )
    order_id = cursor.lastrowid

    for item_id, item in cart.items():
        cursor.execute(
            "INSERT INTO order_items (order_id, menu_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, item_id, item["qty"], item["price"])
        )

    conn.commit()
    cursor.close()
    conn.close()

    session.pop("cart")

    return jsonify({"status": "order placed"})


@app.route("/admin/menu/delete/<int:item_id>")
def delete_menu_item(item_id):
    if not admin_only():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id = %s", (item_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/menu")


# ============================================
# ADMIN DASHBOARD
# PURPOSE:
# Main admin dashboard page (protected)
# ============================================

@app.route("/dashboard")
def admin_dashboard():
    # If not logged in OR not admin → redirect to login
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")

    return render_template("admin_dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

@app.route("/order-success")
def order_success():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("order_success.html")

@app.route("/orders")
def user_orders():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, total_amount, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY id DESC
    """, (session["user_id"],))

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("order_history.html", orders=orders)

@app.route("/admin/orders")
def admin_orders():
    if not admin_only():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.id, u.username, o.total_amount
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
    """)

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_orders.html", orders=orders)


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    result = ai_menu_search(query)
    return jsonify(result)

@app.route("/api/cart/count")
def cart_count():
    """
    PURPOSE:
    - Return total number of items in cart
    - Cart is stored in session (not database)
    """

    cart = session.get("cart", {})

    total_items = 0

    # Sum quantity of all cart items
    for item in cart.values():
        total_items += item["qty"]

    return jsonify({
        "count": total_items
    })




@app.route("/api/ai-description")
def ai_description():
    """
    Generate short (5–7 words) food description
    """

    name = request.args.get("name", "").strip()

    description = generate_short_description(name)

    return jsonify({
        "description": description
    })






# ============================================
# APPLICATION START
# ============================================

if __name__ == "__main__":
    # Initialize database tables
    init_db()

    # Run Flask server in debug mode
    app.run(debug=True)
