document.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", e => {

        if (link.classList.contains("no-transition")) {
            return;
        }

        const href = link.getAttribute("href");
        if (!href || href.startsWith("#") || href.startsWith("http")) return;

        e.preventDefault();

        const transition = document.querySelector(".page-transition");
        if (transition) {
            transition.classList.add("active");
}


        setTimeout(() => {
            window.location.href = href;
        }, 450);
    });
});


/* ================= BOOKING MODAL ================= */
function openBooking() {
    const modal = document.getElementById("bookingModal");
    if (modal) modal.classList.add("active");
}

function closeBooking() {
    const modal = document.getElementById("bookingModal");
    if (modal) modal.classList.remove("active");
}


/* ================= LOAD MENU ================= */
async function loadMenu() {
    try {
        const res = await fetch("/api/menu");
        const menu = await res.json();

        const vegGrid = document.getElementById("vegGrid");
        const nonvegGrid = document.getElementById("nonvegGrid");
        const dessertGrid = document.getElementById("dessertGrid");
        const icecreamGrid = document.getElementById("icecreamGrid");

        // Clear all grids
        vegGrid.innerHTML = "";
        nonvegGrid.innerHTML = "";
        dessertGrid.innerHTML = "";
        icecreamGrid.innerHTML = "";

        menu.forEach(item => {
            const card = `
                <div class="menu-card">
                    <img src="/static/images/${item.image}" alt="${item.name}">
                    <h3>${item.name}</h3>
                    <p>${item.description || "Delicious dish from our kitchen"}</p>
                    <span>₹${item.price}</span>
                    <button class="cart-btn"
                        onclick="addToCart(${item.id}, ${item.price})">
                        Add to Cart
                    </button>
                </div>
            `;

            if (item.category === "veg") {
                vegGrid.innerHTML += card;
            }
            else if (item.category === "nonveg") {
                nonvegGrid.innerHTML += card;
            }
            else if (item.category === "dessert") {
                dessertGrid.innerHTML += card;
            }
            else if (item.category === "icecream") {
                icecreamGrid.innerHTML += card;
            }
        });

    } catch (err) {
        console.error("Menu load failed:", err);
    }
}

/* ================= LOGIN / REGISTER ================= */

function openLogin() {
    const modal = document.getElementById("loginModal");

    // Reset input fields
    document.getElementById("loginUsername").value = "";
    document.getElementById("loginPassword").value = "";

    modal.style.display = "flex";
}


function closeLogin() {
    const modal = document.getElementById("loginModal");

    document.getElementById("loginUsername").value = "";
    document.getElementById("loginPassword").value = "";

    modal.style.display = "none";
}


function openRegister() {
    document.getElementById("registerModal")?.classList.add("active");
}

function closeRegister() {
    document.getElementById("registerModal")?.classList.remove("active");
}

/**
 * Handle user login
 * - Sends credentials to backend
 * - On success: close modal, clear inputs, reload page
 */
function login() {

    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    // Basic frontend validation
    if (!username || !password) {
        alert("Please enter username and password");
        return;
    }

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {

        if (data.success) {

            // Close modal and reset UI
            closeLogin();

            // Small delay for smooth UX
            setTimeout(() => {
                window.location.reload();
            }, 300);

        } else {
            alert(data.message || "Invalid login credentials");
        }

    })
    .catch(err => {
        console.error("Login error:", err);
        alert("Server error. Try again.");
    });
}



async function register() {
    const username = document.getElementById("regUsername").value;
    const password = document.getElementById("regPassword").value;

    const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (data.status === "success") {
        alert("Registered successfully");
        closeRegister();
        openLogin();
    } else {
        alert(data.message);
    }
}


/* ================= CART ================= */
async function addToCart(id, price) {

    const res = await fetch("/api/cart/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: id, price })
    });

    // If user not logged in → redirect
    if (res.status === 401) {
        window.location.href = "/login";
        return;
    }

    const data = await res.json();

    if (data.status === "added") {

        // Show popup message
        showToast("Food added to cart");

        // Update cart count immediately
        loadCartCount();
    }
}

/* =====================================================
   LOAD CART COUNT ON PAGE LOAD
   ===================================================== */

document.addEventListener("DOMContentLoaded", () => {
    loadCartCount();
});



async function loadCart() {
    const res = await fetch("/api/cart");
    const cart = await res.json();

    let total = 0;
    let html = "";

    for (let id in cart) {
        const item = cart[id];
        const itemTotal = item.qty * item.price;
        total += itemTotal;

        html += `
            <div class="cart-item">
                <span>Item ${id} × ${item.qty}</span>
                <span>₹${itemTotal}</span>
            </div>
        `;
    }

    document.getElementById("cartItems").innerHTML = html;
    document.getElementById("cartTotal").innerText = total;
}


function openCart() {
    document.getElementById("cartModal")?.classList.add("active");
}

function closeCart() {
    document.getElementById("cartModal")?.classList.remove("active");
}



function showToast(message) {
    let toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 100);

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
    }, 2500);
}

async function confirmOrder() {
    const res = await fetch("/api/cart");
    const cart = await res.json();

    if (!cart || Object.keys(cart).length === 0) {
        alert("Please select at least 1 item from menu");
        return;
    }

    const orderRes = await fetch("/api/order/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirm: true })
    });

    if (orderRes.ok) {
        alert("Order Successful");
        await clearCart();
    } else {
        alert("Order failed");
    }
}

async function refreshCart() {
    await fetch("/api/cart/clear", { method: "POST" });
    loadCart(); // cart page reload
}

async function clearCart() {
    await fetch("/api/cart/clear", { method: "POST" });
    loadCart();
}



function showCategory(category) {
    const sections = document.querySelectorAll(".menu-category");
    const buttons = document.querySelectorAll(".filter-btn");

    sections.forEach(section => {
        if (category === "all" || section.id === category) {
            section.style.display = "block";
        } else {
            section.style.display = "none";
        }
    });

    buttons.forEach(btn => btn.classList.remove("active"));
    event.target.classList.add("active");
}




async function runSearch() {

    const q = document.getElementById("searchBox").value.trim();
    if (!q) return;

    const wrapper = document.getElementById("searchWrapper");
    const resultsBox = document.getElementById("searchResults");
    const loader = document.getElementById("searchLoader");

    // UI setup before API call
    wrapper.style.display = "block";
    document.querySelector(".menu-section").style.display = "none";
    document.body.classList.add("search-active");

    resultsBox.innerHTML = "";
    loader.style.display = "block"; // SHOW LOADER

    // API call (slow Gemini)
    const res = await fetch("/api/search?q=" + encodeURIComponent(q));
    const data = await res.json();

    loader.style.display = "none"; // HIDE LOADER

    data.forEach(item => {
        resultsBox.innerHTML += `
            <div class="menu-card">
                <img src="/static/images/${item.image}">
                <h3>${item.name}</h3>
                <p>${item.description || "Delicious dish from our kitchen 🍽️"}</p>
                <span>₹${item.price}</span>
                <button onclick="addToCart(${item.id}, ${item.price})">
                    Add to Cart
                </button>
            </div>
        `;
    });

    if (data.length === 0) {
        resultsBox.innerHTML = `<p style="color:#aaa;">No matching dishes found</p>`;
    }
}


/* =====================================================
   CLOSE SEARCH RESULTS
===================================================== */

function closeSearch() {

    // Hide search container
    document.getElementById("searchWrapper").style.display = "none";

    // Show menu again
    document.querySelector(".menu-section").style.display = "block";

    // Enable body scroll again
    document.body.classList.remove("search-active");

    // Clear search input
    document.getElementById("searchBox").value = "";
}


async function loadCartCount() {
    const res = await fetch("/api/cart/count");
    const data = await res.json();

    const countEl = document.getElementById("cartCount");
    if (countEl) {
        countEl.innerText = data.count;
    }
}

/* =========================================================
   BOOKING FORM SUBMIT HANDLER
   PURPOSE:
   - Capture booking form data
   - Send data to Flask backend
   - Show confirmation to user
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    // Get booking form
    const bookingForm = document.getElementById("bookingForm");

    // If booking form exists on page
    if (bookingForm) {

        bookingForm.addEventListener("submit", async function (e) {
            e.preventDefault(); //  Stop page reload

            // Collect user input values
            const bookingData = {
                name: document.getElementById("name").value,
                phone: document.getElementById("phone").value,
                date: document.getElementById("date").value,
                time: document.getElementById("time").value,
                guests: document.getElementById("guests").value
            };

            try {
                // Send booking data to backend API
                const res = await fetch("/api/book-table", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(bookingData)
                });

                const data = await res.json();

                // If booking successful
                if (data.status === "success") {

                    alert("Table booked successfully!");

                    // Close booking modal
                    closeBooking();

                    // Clear form fields
                    bookingForm.reset();

                } else {
                    alert("Booking failed. Please try again.");
                }

            } catch (error) {
                console.error("Booking error:", error);
                alert("Server error. Please try later.");
            }
        });
    }
});

/**
 * Redirect user to home page
 * and trigger login modal automatically
 */
function goToLogin() {
    // Redirect to home with a flag
    window.location.href = "/?login=true";
}

/**
 * Auto open login modal if URL has ?login=true
 * This is used after logout "Login Again" button
 */
document.addEventListener("DOMContentLoaded", function () {

    const params = new URLSearchParams(window.location.search);

    if (params.get("login") === "true") {
        openLogin(); // existing function
    }

});

/**
 * Generate short food description using AI
 */
function generateShortDesc() {
    const foodName = document.getElementById("aiFoodName").value;

    if (!foodName) return;

    fetch(`/api/ai-description?name=${encodeURIComponent(foodName)}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("descInput").value = data.description;
        });
}




