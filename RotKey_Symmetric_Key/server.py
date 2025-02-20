from flask import Flask, request, jsonify, render_template_string
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

app = Flask(__name__)

# Global variable to store the current shared key (bytes)
current_shared_key = None

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
    if not key_hex:
        return jsonify({'error': 'Missing key in payload'}), 400
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
         async function fetchSharedKey(){
             const resp = await fetch("/get-shared-key");
             const data = await resp.json();
             document.getElementById("serverKey").textContent = data.sharedKey ? data.sharedKey : data.error;
         }
         document.getElementById("testForm").addEventListener("submit", async function(e){
             e.preventDefault();
             const plaintext = document.getElementById("plaintext").value;
             const iv = [1,2,3,4,5,6,7,8,9,10,11,12];
             const { encryptedData, iv: usedIV } = await (async () => {
                // For proper testing, you need to perform AES-GCM encryption using the current shared key.
                // For demonstration, we simulate encryption by using the TextEncoder output.
                // In a production scenario, the client should encrypt using the shared key.
                const encoder = new TextEncoder();
                const encoded = encoder.encode(plaintext);
                // Simulate encryption: This is not actual AES-GCM encryption.
                return { encryptedData: Array.from(encoded), iv: iv };
             })();
             const response = await fetch("/decrypt", {
                 method: "POST",
                 headers: {"Content-Type": "application/json"},
                 body: JSON.stringify({ encryptedData: encryptedData, iv: iv })
             });
             const decData = await response.json();
             document.getElementById("output").textContent = decData.decryptedData ? decData.decryptedData : decData.error;
         });
      </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    # Run the Flask server over HTTPS using your self-signed certificate.
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
