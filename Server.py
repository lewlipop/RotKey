from flask import Flask, request, jsonify
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

if __name__ == '__main__':
    # Run the Flask server over HTTPS using your self-signed certificate.
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
                                                                                                           
┌──(kali㉿kali)-[~/rotkey]
└─$ 
                                                                                                           
┌──(kali㉿kali)-[~/rotkey]
└─$ ls -l            
total 28
-rw-rw-r-- 1 kali kali 3859 Feb 12 14:00 app.py
-rw-rw-r-- 1 kali kali 2017 Feb 16 02:48 cert.pem
-rw------- 1 kali kali 3272 Feb 16 02:48 key.pem
-rw-rw-r-- 1 kali kali 5320 Feb 13 12:04 newapp.py
-rw-rw-r-- 1 kali kali 2880 Feb 16 04:32 newECDH.py
drwxrwxr-x 5 kali kali 4096 Feb 12 13:04 venv
                                                                                                           
┌──(kali㉿kali)-[~/rotkey]
└─$ nano newECDH.py
                                                                                                           
┌──(kali㉿kali)-[~/rotkey]
└─$ cat newECDH.py
from flask import Flask, request, jsonify
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

if __name__ == '__main__':
    # Run the Flask server over HTTPS using your self-signed certificate. 
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem')) // This shit needa change because I self generated the cert
