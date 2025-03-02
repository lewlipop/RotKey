from flask import Flask, request, redirect, session, jsonify, render_template_string, render_template
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import mysql.connector
import re
import bcrypt
import ssl
import hashlib
import json

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

@app.route('/')
def home():
    return render_template('index.html')


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/update-key', methods=['POST'])
def update_key():
    global current_shared_key
    data = request.get_json()
    key_hex = data.get('key')
    if key_hex is None:
        current_shared_key = None
        print("Shared key deleted.")
        return jsonify({'status': 'Key deleted successfully'})
    try:
        current_shared_key = bytes.fromhex(key_hex)
        print("Updated shared key (hex):", key_hex)
        return jsonify({'status': 'Key updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    if current_shared_key is None:
        return jsonify({'error': 'Shared key not established'}), 400
    data = request.get_json()
    encrypted_data_list = data.get('encryptedData')
    iv_list = data.get('iv')
    if not encrypted_data_list or not iv_list:
        return jsonify({'error': 'Missing encrypted data or IV'}), 400
    try:
        ciphertext = bytes(encrypted_data_list)
        iv = bytes(iv_list)
        print("Decrypting with key (hex):", current_shared_key.hex())
        print("IV (hex):", iv.hex())
        print("Ciphertext (hex):", ciphertext.hex())
        aesgcm = AESGCM(current_shared_key)
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        return jsonify({'decryptedData': plaintext.decode('utf-8')})
    except Exception as e:
        print("Decryption error:", e)
        return jsonify({'error': str(e) if str(e) else "Unknown decryption error"}), 500

@app.route('/get-shared-key', methods=['GET'])
def get_shared_key():
    if current_shared_key:
        return jsonify({"sharedKey": current_shared_key.hex()})
    else:
        return jsonify({"error": "Shared key not established"}), 400

@app.route('/test')
def test_page():
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>RotKey Server Test</title>
      <style>
         body { font-family: sans-serif; margin: 20px; }
         pre { background: #f0f0f0; padding: 10px; }
         input, button { margin: 5px; }
      </style>
    </head>
    <body>
      <h1>RotKey Server Test Page</h1>
      <p>Current Shared Key (Server view): <span id="serverKey">Not established</span></p>
      <button onclick="fetchSharedKey()">Fetch Current Shared Key</button>
      <hr>
      <form id="testForm">
         <label>Plaintext: <input type="text" id="plaintext" required /></label>
         <button type="submit">Encrypt & Decrypt</button>
      </form>
      <h2>Decrypted Output</h2>
      <pre id="output">Awaiting submission...</pre>
      <script>
         function hexToArrayBuffer(hex) {
             const typedArray = new Uint8Array(hex.match(/[\da-f]{2}/gi).map(h => parseInt(h, 16)));
             return typedArray.buffer;
         }
         async function importKeyFromHex(hex) {
             const keyBuffer = hexToArrayBuffer(hex);
             return await window.crypto.subtle.importKey(
                 "raw",
                 keyBuffer,
                 { name: "AES-GCM" },
                 false,
                 ["encrypt", "decrypt"]
             );
         }
         async function encryptWithKey(plaintext, key, iv) {
             const encoder = new TextEncoder();
             const encoded = encoder.encode(plaintext);
             return await window.crypto.subtle.encrypt(
                 { name: "AES-GCM", iv: iv },
                 key,
                 encoded
             );
         }
         async function fetchSharedKey(){
             const resp = await fetch("/get-shared-key");
             const data = await resp.json();
             document.getElementById("serverKey").textContent = data.sharedKey ? data.sharedKey : data.error;
             return data.sharedKey;
         }
         document.getElementById("testForm").addEventListener("submit", async function(e){
             e.preventDefault();
             const plaintext = document.getElementById("plaintext").value;
             const iv = crypto.getRandomValues(new Uint8Array(12));

             const sharedKeyHex = await fetchSharedKey();
             if(!sharedKeyHex){
                 document.getElementById("output").textContent = "Shared key not available.";
                 return;
             }
             let cryptoKey;
             try {
                 cryptoKey = await importKeyFromHex(sharedKeyHex);
             } catch(err) {
                 document.getElementById("output").textContent = "Error importing key: " + err;
                 return;
             }
             let ciphertextBuffer;
             try {
                 ciphertextBuffer = await encryptWithKey(plaintext, cryptoKey, iv);
             } catch(err) {
                 document.getElementById("output").textContent = "Encryption error: " + err;
                 return;
             }
             const ciphertextArray = Array.from(new Uint8Array(ciphertextBuffer));
             const response = await fetch("/decrypt", {
                 method: "POST",
                 headers: {"Content-Type": "application/json"},
                 body: JSON.stringify({ encryptedData: ciphertextArray, iv: Array.from(iv) })
             });
             const result = await response.json();
             document.getElementById("output").textContent = result.decryptedData ? result.decryptedData : result.error;
         });
      </script>
    </body>
    </html>
    '''
    return html

@app.route('/process_register', methods=['POST'])
def register():
    data = request.get_json()

    if 'encryptedData' in data and 'iv' in data:
        # Encrypted data received, proceed with decryption
        if current_shared_key is None:
            return jsonify({'success': False, 'message': 'Shared key not established'}), 400

        encrypted_data_list = data.get('encryptedData')
        iv_list = data.get('iv')
        if not encrypted_data_list or not iv_list:
            return jsonify({'success': False, 'message': 'Missing encrypted data or IV'}), 400

        try:
            ciphertext = bytes(encrypted_data_list)
            iv = bytes(iv_list)
            print("Decrypting with key (hex):", current_shared_key.hex())
            print("IV (hex):", iv.hex())
            print("Ciphertext (hex):", ciphertext.hex())
            aesgcm = AESGCM(current_shared_key)
            decrypted_data = aesgcm.decrypt(iv, ciphertext, None)
            
            decrypted_json = decrypted_data.decode('utf-8')
            print("Decrypted JSON string:", decrypted_json)
            data = json.loads(decrypted_json)
            print("here:", data)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Decryption error: {str(e)}'}), 500
    else:
        # Data is not encrypted, use it directly
        print("Received unencrypted data:", data)

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
    print(hashed_password)

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        (user_exists,) = cursor.fetchone()
        if user_exists:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        # Check if the email already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        (email_exists,) = cursor.fetchone()
        if email_exists:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400

        # Insert new user
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        conn.commit()

        return jsonify({'success': True, 'message': 'Registration successful'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/process_login', methods=['POST'])
def login():
    data = request.get_json()

    if 'encryptedData' in data and 'iv' in data:
        # Encrypted data received, proceed with decryption
        if current_shared_key is None:
            return jsonify({'success': False, 'message': 'Shared key not established'}), 400

        encrypted_data_list = data.get('encryptedData')
        iv_list = data.get('iv')
        if not encrypted_data_list or not iv_list:
            return jsonify({'success': False, 'message': 'Missing encrypted data or IV'}), 400

        try:
            ciphertext = bytes(encrypted_data_list)
            iv = bytes(iv_list)
            print("Decrypting with key (hex):", current_shared_key.hex())
            print("IV (hex):", iv.hex())
            print("Ciphertext (hex):", ciphertext.hex())
            aesgcm = AESGCM(current_shared_key)
            decrypted_data = aesgcm.decrypt(iv, ciphertext, None)
            
            decrypted_json = decrypted_data.decode('utf-8')
            print("Decrypted JSON string:", decrypted_json)
            data = json.loads(decrypted_json)
            print("here:", data)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Decryption error: {str(e)}'}), 500
    else:
        # Data is not encrypted, use it directly
        print("Received unencrypted data:", data)

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and Password are required'}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get the user details based on email
        cursor.execute("SELECT idUsers, username, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        user_id, username, hashed_password = user

        # Check if the password matches
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        # If login is successful, set session (optional)
        session['user'] = username  # Uncomment if using sessions

        return jsonify({'success': True, 'message': 'Login successful', 'username': username}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000, debug=True)
