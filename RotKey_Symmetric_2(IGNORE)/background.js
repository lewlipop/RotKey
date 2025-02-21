// background.js (Manifest V2 persistent background script)
console.log("Background script loaded.");

let encryptionEnabled = false;
const rotationInterval = 300; // seconds (5 minutes)
let rotationIntervalId = null;
let keyRotationInProgress = false;
const serverUrl = "https://192.168.86.30:5000";  // Hardcoded server URL

// Fixed IV for testing (12 bytes for AES-GCM)
const fixedIV = [1,2,3,4,5,6,7,8,9,10,11,12];

// Generate a random symmetric key (256-bit)
async function generateRandomSymmetricKey() {
  console.log("Generating random symmetric key...");
  const keyBytes = new Uint8Array(32); // 32 bytes = 256 bits
  crypto.getRandomValues(keyBytes);
  console.log("Random symmetric key generated:", keyBytes);
  return keyBytes;
}

// Convert an array of bytes to a hexadecimal string.
function bytesToHex(bytes) {
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

// Update the server with the new symmetric key via the /update-key endpoint.
async function updateServerKey(keyHex) {
  try {
    console.log("Updating server with new key at:", serverUrl);
    const response = await fetch(`${serverUrl}/update-key`, {
      method: "POST",
      mode: "cors", // explicitly set CORS mode
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: keyHex })
    });
    console.log("Response status from update-key:", response.status);
    const data = await response.json();
    if (data.error) {
      console.error("Server error on key update:", data.error);
    } else {
      console.log("Server key updated successfully:", data.status);
    }
  } catch (err) {
    console.error("Error during key update fetch:", err);
  }
}

// Perform a handshake check with the server.
// Returns true if the server responds with status "ok", false otherwise.
async function performHandshake() {
  console.log("Performing handshake with", serverUrl + "/rotkey-handshake");
  try {
    const response = await fetch(`${serverUrl}/rotkey-handshake`, {
      method: "GET",
      mode: "cors"
    });
    if (!response.ok) throw new Error("Non-200 response");
    const data = await response.json();
    console.log("Handshake response:", data);
    return data.status === "ok";
  } catch (e) {
    console.error("Handshake error:", e);
    return false;
  }
}

// Initiate key rotation: generate a new symmetric key and update storage and server.
async function initiateKeyRotation() {
  console.log("Initiating key rotation...");
  if (keyRotationInProgress) {
    console.log("Key rotation already in progress; skipping.");
    return;
  }
  keyRotationInProgress = true;
  try {
    const keyBytes = await generateRandomSymmetricKey();
    const keyHex = bytesToHex(keyBytes);
    console.log("New symmetric key (hex):", keyHex);
    // Store the new key, fixed IV, and timestamp.
    chrome.storage.local.set({
      sharedKey: keyHex,
      fixedIV: fixedIV,
      lastRotation: Date.now()
    });
    // Update the server with the new key.
    await updateServerKey(keyHex);
  } catch (e) {
    console.error("Error during key rotation:", e);
  }
  keyRotationInProgress = false;
}

// Start encryption and key rotation.
// This function will first perform a handshake check with the server.
// If the handshake fails, key rotation will not start.
async function startEncryption() {
  console.log("Starting encryption...");
  const handshakeOk = await performHandshake();
  if (!handshakeOk) {
    console.error("Handshake failed. Server is not compatible. Aborting key rotation.");
    return;
  }
  encryptionEnabled = true;
  const now = Date.now();
  chrome.storage.local.set({
    encryptionEnabled: true,
    lastRotation: now
  });
  await initiateKeyRotation();
  rotationIntervalId = setInterval(() => {
    if (encryptionEnabled) {
      console.log("Rotating key...");
      initiateKeyRotation();
      chrome.storage.local.set({ lastRotation: Date.now() });
    }
  }, rotationInterval * 1000);
  console.log("Encryption started at", now);
}

// Stop encryption and key rotation.
function stopEncryption() {
  console.log("Stopping encryption...");
  encryptionEnabled = false;
  chrome.storage.local.set({ encryptionEnabled: false });
  if (rotationIntervalId) {
    clearInterval(rotationIntervalId);
    rotationIntervalId = null;
  }
  console.log("Encryption stopped.");
}

// Listen for messages from the popup.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Received message in background:", message);
  if (message.action === "startEncryption") {
    startEncryption().then(() => {
      sendResponse({ status: "started" });
    });
  } else if (message.action === "stopEncryption") {
    stopEncryption();
    sendResponse({ status: "stopped" });
  }
  return true;
});
