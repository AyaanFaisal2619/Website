import sqlite3
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = '12345'  # Replace with a secure secret key

# User Registration and Login Routes

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password for security (you should use a stronger hashing algorithm in production)
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Store the user's data in the database (replace with your database code)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        # Redirect to the login page after registration
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the provided password and compare it with the stored hash
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Check if the user exists and the password is correct (replace with your database code)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Store the username in the session to track the user's login status
            session['username'] = username
            return redirect(url_for('listings'))

    return render_template('login.html')

# Route for user logout
@app.route('/logout')
def logout():
    # Clear the session data to log the user out
    session.pop('username', None)
    return redirect(url_for('login'))

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the listings page
@app.route('/listings')
def listings():
    # Check if the user is logged in
    if 'username' in session:
        # Retrieve listings from the database (replace with your database code)
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM listings')
        listings = cursor.fetchall()
        conn.close()

        return render_template('listings.html', listings=listings, username=session['username'])
    
    # If the user is not logged in, redirect to the login page
    return redirect(url_for('login'))

# Route for adding a new listing
@app.route('/add_listing', methods=['POST'])
def add_listing():
    if 'username' in session:
        game = request.form['game']
        item_name = request.form['item_name']
        price = request.form['price']

        # Store the new listing in the database (replace with your database code)
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO listings (game, item_name, price) VALUES (?, ?, ?)', (game, item_name, price))
        conn.commit()
        conn.close()

    return redirect(url_for('listings'))

if __name__ == '__main__':
    app.run(debug=True)
