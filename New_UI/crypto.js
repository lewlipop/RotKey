// AES-GCM Encryption/Decryption Functions
async function generateKey() {
    return await crypto.subtle.generateKey(
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    );
  }
  
  async function encryptData(data, key) {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encodedData = new TextEncoder().encode(data);
    const encryptedData = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      key,
      encodedData
    );
    return { encryptedData, iv };
  }
  
  async function decryptData(encryptedData, key, iv) {
    const decryptedData = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv },
      key,
      encryptedData
    );
    return new TextDecoder().decode(decryptedData);
  }
  
  // ECDH Key Exchange Functions
  async function generateECDHKeyPair() {
    return await crypto.subtle.generateKey(
      { name: "ECDH", namedCurve: "P-256" },
      true,
      ["deriveKey", "deriveBits"]
    );
  }
  
  async function deriveSharedSecret(privateKey, publicKey) {
    return await crypto.subtle.deriveKey(
      {
        name: "ECDH",
        public: publicKey
      },
      privateKey,
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    );
  }
  
  async function exportPublicKey(publicKey) {
    const exported = await crypto.subtle.exportKey("spki", publicKey);
    return btoa(String.fromCharCode(...new Uint8Array(exported)));
  }
  
  async function importServerPublicKey(pem) {
    const binaryDer = Uint8Array.from(atob(pem), c => c.charCodeAt(0));
    return await crypto.subtle.importKey(
      "spki",
      binaryDer,
      { name: "ECDH", namedCurve: "P-256" },
      true,
      []
    );
  }
  