from flask import Flask, request, jsonify, render_template_string
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

app = Flask(__name__)

# Generate the server's ECDH key pair on startup.
server_private_key = ec.generate_private_key(ec.SECP256R1())
server_public_key = server_private_key.public_key()

# Global variable to store the current shared key (bytes).
current_shared_key = None

def serialize_public_key(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(pem).decode('utf-8')

@app.route('/initiate-key-exchange', methods=['POST'])
def initiate_key_exchange():
    global current_shared_key
    data = request.get_json()
    client_public_key_b64 = data.get('publicKey')
    if not client_public_key_b64:
        return jsonify({'error': 'Missing client public key'}), 400
    try:
        # Decode client's public key (base64-encoded PEM).
        client_public_key_pem = base64.b64decode(client_public_key_b64)
        client_public_key = serialization.load_pem_public_key(client_public_key_pem)
        # Perform ECDH exchange to derive the shared secret.
        shared_secret = server_private_key.exchange(ec.ECDH(), client_public_key)
        # Derive a 256-bit AES key from the shared secret.
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'RotKey'
        ).derive(shared_secret)
        current_shared_key = derived_key
        print("Derived shared key (hex):", derived_key.hex())
        return jsonify({'serverPublicKey': serialize_public_key(server_public_key)})
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
        aesgcm = AESGCM(current_shared_key)
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        return jsonify({'decryptedData': plaintext.decode('utf-8')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test_page():
    # The test page HTML with embedded JavaScript to test the full flow.
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>RotKey Complete Test</title>
      <style>
        body { font-family: sans-serif; margin: 20px; }
        pre { background: #f0f0f0; padding: 10px; }
        button { margin: 5px 0; }
      </style>
    </head>
    <body>
      <h1>RotKey Complete Test</h1>
      <button id="startKeyExchange">Start Key Exchange</button>
      <div id="exchangeStatus"></div>
      <hr>
      <form id="testForm">
        <label>Username: <input type="text" id="username" required /></label><br><br>
        <label>Password: <input type="password" id="password" required /></label><br><br>
        <button type="submit">Encrypt & Decrypt</button>
      </form>
      <h2>Decrypted Output</h2>
      <pre id="output">Awaiting submission...</pre>
      
      <script>
      // Global variable to store the derived shared key (as CryptoKey) in client JS.
      let sharedCryptoKey = null;
      
      // Generate an ECDH key pair using Web Crypto API.
      async function generateECDHKeyPair() {
        return await crypto.subtle.generateKey(
          { name: "ECDH", namedCurve: "P-256" },
          true,
          ["deriveKey", "deriveBits"]
        );
      }
      
      // Export public key as a base64 encoded PEM string.
      async function exportPublicKey(publicKey) {
        const exported = await crypto.subtle.exportKey("spki", publicKey);
        const uint8Array = new Uint8Array(exported);
        let binary = "";
        for (let i = 0; i < uint8Array.byteLength; i++) {
          binary += String.fromCharCode(uint8Array[i]);
        }
        return btoa(binary);
      }
      
      // Import server's public key from base64 PEM.
      async function importServerPublicKey(serverKeyB64) {
        const binaryString = atob(serverKeyB64);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        return await crypto.subtle.importKey(
          "spki",
          bytes.buffer,
          { name: "ECDH", namedCurve: "P-256" },
          true,
          []
        );
      }
      
      // Derive a shared AES-GCM key using ECDH.
      async function deriveSharedKey(clientPrivateKey, serverPublicKey) {
        return await crypto.subtle.deriveKey(
          { name: "ECDH", public: serverPublicKey },
          clientPrivateKey,
          { name: "AES-GCM", length: 256 },
          true,
          ["encrypt", "decrypt"]
        );
      }
      
      // Export a CryptoKey as a hex string.
      async function exportKeyToHex(cryptoKey) {
        const raw = await crypto.subtle.exportKey("raw", cryptoKey);
        const uint8Array = new Uint8Array(raw);
        return Array.from(uint8Array).map(b => b.toString(16).padStart(2, '0')).join('');
      }
      
      // Function to initiate key exchange with the server.
      async function startKeyExchange() {
        const statusDiv = document.getElementById("exchangeStatus");
        statusDiv.textContent = "Generating key pair...";
        try {
          const keyPair = await generateECDHKeyPair();
          const clientPublicKeyB64 = await exportPublicKey(keyPair.publicKey);
          statusDiv.textContent = "Sending client public key to server...";
          // Send client public key to server's /initiate-key-exchange endpoint.
          const response = await fetch("/initiate-key-exchange", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ publicKey: clientPublicKeyB64 })
          });
          const data = await response.json();
          if (data.error) {
            statusDiv.textContent = "Error: " + data.error;
            return;
          }
          statusDiv.textContent = "Received server public key.";
          const serverPublicKey = await importServerPublicKey(data.serverPublicKey);
          // Derive shared AES-GCM key.
          sharedCryptoKey = await deriveSharedKey(keyPair.privateKey, serverPublicKey);
          const sharedKeyHex = await exportKeyToHex(sharedCryptoKey);
          statusDiv.textContent = "Key exchange complete. Derived shared key (hex): " + sharedKeyHex;
        } catch (e) {
          statusDiv.textContent = "Key exchange failed: " + e;
          console.error(e);
        }
      }
      
      // Event listener for "Start Key Exchange" button.
      document.getElementById("startKeyExchange").addEventListener("click", async () => {
        await startKeyExchange();
      });
      
      // Encrypt form data using the derived shared key, then send to /decrypt endpoint.
      document.getElementById("testForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!sharedCryptoKey) {
          alert("Please start key exchange first.");
          return;
        }
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const plaintext = "Username: " + username + "\nPassword: " + password;
        // Use a fixed IV for testing (12 bytes).
        const iv = new Uint8Array([1,2,3,4,5,6,7,8,9,10,11,12]);
        try {
          const encoder = new TextEncoder();
          const encoded = encoder.encode(plaintext);
          const ciphertextBuffer = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            sharedCryptoKey,
            encoded
          );
          const ciphertextArray = Array.from(new Uint8Array(ciphertextBuffer));
          // Send ciphertext to /decrypt endpoint.
          const resp = await fetch("/decrypt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ encryptedData: ciphertextArray, iv: Array.from(iv) })
          });
          const result = await resp.json();
          document.getElementById("output").textContent = result.decryptedData ? result.decryptedData : result.error;
        } catch (err) {
          document.getElementById("output").textContent = "Encryption error: " + err;
          console.error(err);
        }
      });
      </script>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    # Run the Flask server over HTTPS using your self-signed certificate.
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
