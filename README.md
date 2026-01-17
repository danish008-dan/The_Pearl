## The Pearl – AI Powered Restaurant Web Application
AI powered restaurant web application using Flask, MySQL and Google Gemini API

## Overview

The Pearl is a full-stack AI-powered restaurant web application built using Flask, MySQL, HTML, CSS, and JavaScript, integrated with Google Gemini AI.

The project allows users to browse a restaurant menu, search food items using natural language, place orders, manage a cart, and book tables.
Admins can manage menu items, users, bookings, and orders through a protected admin dashboard.
AI is used to enhance food search and generate smart menu descriptions.

This project demonstrates real-world backend logic, database integration, session handling, AI usage, and clean frontend-backend communication.

## Key Features
## User Features

  > User registration and login system
  > Secure session-based authentication
  > Browse full restaurant menu
  > AI-powered natural language food search
  > Add items to cart
  > Cart quantity management
  > Place food orders
  > Order history
  > Table booking system

## Admin Features

  > Secure admin login
  > Admin dashboard
  > Add, delete, and manage menu items
  > AI-generated short food descriptions
  > View all users
  > View all bookings
  > View all orders
  > Role-based access control (Admin / User)

## AI Features (Google Gemini)

  > Natural language menu search
  > Smart food recommendation
  > AI-generated short menu descriptions (5–7 words)
  > Robust error handling for AI failures

### Tech Stack

## Frontend

  > HTML5
  > CSS3
  > JavaScript (Vanilla JS)
  > Fetch API

## Backend

  > Python (Flask)
  > MySQL / MariaDB
  > Session-based authentication

## AI Integration

  > Google Gemini API

## Tools & Libraries

  > Flask
  > Werkzeug (password hashing)
  > python-dotenv
  > Google Generative AI SDK

## Project Folder Structure

The_Pearl/
│
├── app.py
│
├── db.py
│
├── ai/
│   ├── nlp_search_gemini.py
│   └── ai_description_gemini.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── images/
│       └── .gitkeep
│
├── templates/
│   ├── index.html
│   ├── menu.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── order_success.html
│   ├── order_history.html
│   ├── admin_dashboard.html
│   ├── admin_menu.html
│   ├── admin_users.html
│   ├── admin_orders.html
│   ├── admin_bookings.html
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md

### Database Structure
## Users Table
users
- id (INT, PRIMARY KEY)
- username (VARCHAR, UNIQUE)
- password (VARCHAR, HASHED)
- role (ENUM: user, admin)
- created_at (TIMESTAMP)

## Menu Table
menu
- id
- name
- description
- price
- image
- category

## Orders Tables
orders
- id
- user_id
- total_amount
- created_at

order_items
- id
- order_id
- menu_id
- quantity
- price

## Bookings Table
bookings
- id
- name
- phone
- booking_date
- booking_time
- guests

## Environment Variables (.env)
Create a .env file in the root directory:
  > SECRET_KEY=your_secret_key_here
  > GEMINI_API_KEY=your_gemini_api_key_here

## Installation & Setup
1. Clone the Repository
git clone https://github.com/yourusername/the-pearl.git
cd the-pearl

2. Create Virtual Environment
python -m venv .venv
source .venv/bin/activate   (Linux / Mac)
.venv\Scripts\activate      (Windows)

3. Install Dependencies
pip install -r requirements.txt

4. Setup Database

Create a MySQL database

Update database credentials in db.py

Required tables are auto-created on first run

5. Run Application
python app.py
Server will run on:
  > http://127.0.0.1:5000

## Security Features

  > Password hashing using Werkzeug
  > Session-based authentication
  > Admin-only route protection
  > API input validation
  > AI error fallback handling

## AI Error Handling
If Gemini API fails or returns unexpected output:

  > Application safely falls back to default descriptions
  > Frontend functionality remains unaffected
  > No crash or broken UI

## Future Enhancements

  > Payment gateway integration
  > User profile management
  > Image upload support
  > Order status tracking
  > Advanced AI personalization
  > Mobile responsive UI improvements

## Use Case
This project is ideal for:

  > Full-stack portfolio showcase
  > AI integration demonstration
  > Restaurant management system prototype
  > Flask + MySQL learning reference

### Author
Danish Khatri

Full Stack Developer
Python | Flask | MySQL | AI Integration

## License
This project is licensed for educational and portfolio use.
