from flask import Flask, request, redirect, session, jsonify, render_template_string, render_template
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import mysql.connector
import re
import bcrypt
import ssl
import hashlib

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'whatKeyisIt'

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1", 
            user="ict2214P2BG4", 
            password="R0tk3yIct2214", 
            database="rotkey",
            ssl_disabled=True
        )
        if conn.is_connected():
            print("Successfully connected to the database!")
        return conn

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Password validation regex
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")


# Global variable to store the current shared key (bytes)
current_shared_key = None

@app.route('/process_register', methods=['POST'])
def register():
#    print(ssl.OPENSSL_VERSION)

    data = request.get_json()

    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

#    print(email)
#    print(username)
#    print(password)

    # Validate fields
    if not email or not username or not password:
#        print("hello")
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
#        print("hello")
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400

    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
#        print("hello")
        return jsonify({'success': False, 'message': 'Username contains invalid characters'}), 400

    if not PASSWORD_REGEX.match(password):
#        print("hello")
        return jsonify({'success': False, 'message': 'Password does not meet security requirements'}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(hashed_password)

    conn = None
    cursor = None

    try:
#       print("Calling get_db_connection()...")
        conn = get_db_connection()       
        cursor = conn.cursor()

	# Check if the username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        (user_exists,)=cursor.fetchone()
        if user_exists:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        # Check if the email already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        (email_exists,)=cursor.fetchone()
        if email_exists:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400



#        print(cursor)

        # Insert new user
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        conn.commit()

        return jsonify({'success': True, 'message': 'Registration successful'}), 201

    #except mysql.connector.IntegrityError:
     #   return jsonify({'success': False, 'message': 'Email already exists'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/process_login', methods=['POST'])
def login():
    data = request.get_json()  # Parse JSON data from request

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

#    print(email)
#    print(password)
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and Password are required'}), 400

    conn = None
    cursor = None

    try:
#        print("Calling get db connection()...")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get the user details based on email
        cursor.execute("SELECT idUsers, username, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
#            print("h1")
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        user_id, username, hashed_password = user

        # Check if the password matches
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
#            print("h2")
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        #If login is successful, set session (optional)
#        print("h3")
        session['user'] = username  # Uncomment if using sessions

        return jsonify({'success': True, 'message': 'Login successful', 'username': username}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()