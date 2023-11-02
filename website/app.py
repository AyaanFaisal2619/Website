import sqlite3
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '12345'  # Replace with a secure secret key
USERS_DATABASE = 'users.db'
LISTINGS_DATABASE = 'listings.db'

# Create the SQLite databases for users and listings
def create_databases():
    try:
        # Create the users database
        conn_users = sqlite3.connect(USERS_DATABASE)
        cursor_users = conn_users.cursor()

        cursor_users.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn_users.commit()
        conn_users.close()

        # Create the listings database
        conn_listings = sqlite3.connect(LISTINGS_DATABASE)
        cursor_listings = conn_listings.cursor()

        cursor_listings.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price REAL NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn_listings.commit()
        conn_listings.close()

        return True
    except Exception as e:
        return str(e)

# Initialize the databases
if not create_databases():
    print("Error creating the databases:", create_databases())

# Homepage route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect(USERS_DATABASE)
            cursor = conn.cursor()

            # Check if the username is already taken
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                flash('Username already taken. Please choose another.', 'error')
            else:
                # Insert the new user into the database with the hashed password
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
                conn.close()
                flash('Registration successful. You can now log in.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred during registration.', 'error')
            print("Error during registration:", str(e))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            conn = sqlite3.connect(USERS_DATABASE)
            cursor = conn.cursor()

            # Retrieve the user's data from the database
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user:
                stored_password = user[2]
                # Verify the entered password against the hashed password
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    # Passwords match
                    session['username'] = username
                    flash('Login successful.', 'success')
                    conn.close()
                    return redirect(url_for('add_listing'))
                else:
                    flash('Incorrect password. Please try again.', 'error')
            else:
                flash('Username not found. Please register.', 'error')
        except Exception as e:
            flash('An error occurred during login.', 'error')
            print("Error during login:", str(e))
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Listings route (requires authentication)
@app.route('/add_listing', methods=['POST','GET'])
def add_listing():
    if 'username' not in session:
        flash('You must log in to access this page.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
        # Your code here
    
            try:
            
                game = request.form['game']
                item_name = request.form['item_name']
                price = request.form['price']

                conn = sqlite3.connect(LISTINGS_DATABASE)
                cursor = conn.cursor()

                # Get the user ID based on the username from the session
                cursor.execute('SELECT id FROM users WHERE username = ?', (session['username'],))
                user_id = cursor.fetchone()[0]

                # Insert the listing data into the database
                cursor.execute('INSERT INTO listings (game, item_name, price, user_id) VALUES (?, ?, ?, ?)',
                            (game, item_name, price, user_id))
                
                conn.commit()
                flash('Listing added successfully.', 'success')
            except Exception as e:
                conn.rollback()  # Rollback changes in case of an error
                flash(f'Error adding the listing: {str(e)}', 'error')
            finally:
                conn.close()
        except Exception as e:
            print(f"Error: {str(e)}")
            print("hello")

    # Retrieve listings from the database
    try:
        conn = sqlite3.connect(LISTINGS_DATABASE)
        cursor = conn.cursor()

        # Query to fetch listings along with usernames of sellers
        cursor.execute('''
            SELECT listings.id, listings.game, listings.item_name, listings.price, users.username
            FROM listings
            INNER JOIN users ON listings.user_id = users.id
        ''')
        listings_data = cursor.fetchall()
        conn.close()
    except Exception as e:
        flash(f'Error retrieving listings: {str(e)}', 'error')
        listings_data = []

    return render_template('listings.html', listings=listings_data)

if __name__ == '__main__':
    app.run(debug=False)
