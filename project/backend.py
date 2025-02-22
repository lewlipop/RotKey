from flask import Flask, request, jsonify, render_template, render_template_string
import mysql.connector
import re
import bcrypt

app = Flask(__name__)


# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="23.102.235.79",
        user="ict2214P2BG4",
        password="R0tk3yIct2214",
        database="rotkey"
    )

# Password validation regex
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

@app.route('/process_register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # Validate fields
    if not email or not username or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400

    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return jsonify({'success': False, 'message': 'Username contains invalid characters'}), 400

    if not PASSWORD_REGEX.match(password):
        return jsonify({'success': False, 'message': 'Password does not meet security requirements'}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new user
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        conn.commit()

        return jsonify({'success': True, 'message': 'Registration successful'}), 201

    except mysql.connector.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already exists'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

