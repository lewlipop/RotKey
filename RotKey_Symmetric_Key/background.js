// background.js (Manifest V2 persistent background script)
console.log("Background script loaded.");

let encryptionEnabled = false;
const rotationInterval = 300; // seconds (5 minutes)
let rotationIntervalId = null;
let keyRotationInProgress = false;

// Fixed IV for testing (12 bytes for AES-GCM)
const IV = crypto.getRandomValues(new Uint8Array(12));

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
    let serverUrl;
    await new Promise((resolve) => {
      chrome.storage.local.get("serverUrl", (result) => {
        serverUrl = result.serverUrl || "https://p2bg4rotkey-ict2214.zapto.org";
        resolve();
      });
    });
    console.log("Updating server with new key at:", serverUrl);

    // Handle empty key case
    const body = keyHex ? JSON.stringify({ key: keyHex }) : JSON.stringify({ key: null });

    const response = await fetch(`${serverUrl}/update-key`, {
      method: "POST",
      mode: "cors",
      headers: { "Content-Type": "application/json" },
      body: body
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

// Initiate key rotation: generate a new symmetric key, store it, and update the server.
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
      IV: IV,
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
function startEncryption() {
  console.log("Starting encryption...");
  encryptionEnabled = true;
  const now = Date.now();
  chrome.storage.local.set({
    encryptionEnabled: true,
    lastRotation: now
  });
  initiateKeyRotation();
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

// Listen for messages from the popup or webpage.
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  console.log("Received message in background:", message);
  if (message.action === "startEncryption") {
    startEncryption();
    sendResponse({ status: "started" });
  } else if (message.action === "stopEncryption") {
    stopEncryption();
    sendResponse({ status: "stopped" });
  }
  return true;
});

// Listen for messages from external sources (e.g., webpage).
chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
  console.log("Received external message in background:", message);
  if (message.action === "checkKeyRotation") {
    console.log("Checking key rotation status...");
    if (encryptionEnabled) {
      sendResponse({ status: "active" });
    } else {
      sendResponse({ status: "inactive" });
    }
  } else if (message.action === "updateKey") {
    // Update the server with the current key
    console.log("Received updateKey message.");
    chrome.storage.local.get("sharedKey", async (result) => {
      const keyHex = result.sharedKey;
      if (keyHex) {
        await updateServerKey(keyHex);
        sendResponse({ status: "key updated" });
      } else {
        sendResponse({ status: "no key found" });
      }
    });
  } else if (message.action === "deleteKey") {
    // Update the server with an empty key to delete it
    console.log("Received deleteKey message.");
    await updateServerKey("");
    sendResponse({ status: "key deleted" });
  }
  return true;
});
