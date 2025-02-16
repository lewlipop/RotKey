// background.js (Manifest V2 persistent background page)

let encryptionEnabled = false;
const rotationInterval = 300; // seconds (5 minutes)
let rotationIntervalId = null;
let currentSharedKey = null; // For demonstration: current shared key (should be securely stored!)

async function generateRandomKey() {
  // For demonstration, generate a random 32-byte key using crypto.getRandomValues
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return array;
}

async function initiateKeyExchange() {
  // In your real logic, this would perform an ECDH exchange.
  // For demo purposes, let's generate a random key to represent the new shared key.
  currentSharedKey = await generateRandomKey();

  // For demonstration, convert the key to hex so it can be shown easily.
  const keyHex = Array.from(currentSharedKey)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
  console.log("Key exchange initiated. New key:", keyHex);

  // Store the new key and the rotation time in chrome.storage (for demo only)
  chrome.storage.local.set({
    sharedKey: keyHex,
    lastRotation: Date.now()
  });

  // Here you would also perform your fetch call to your server for key exchange.
}

// Start encryption: set flag, store state, and set up recurring rotations.
function startEncryption() {
  encryptionEnabled = true;
  const now = Date.now();
  chrome.storage.local.set({
    encryptionEnabled: true,
    lastRotation: now
  });
  initiateKeyExchange();
  rotationIntervalId = setInterval(() => {
    if (encryptionEnabled) {
      initiateKeyExchange();
      chrome.storage.local.set({ lastRotation: Date.now() });
    }
  }, rotationInterval * 1000);
  console.log("Encryption started at " + now);
}

// Stop encryption: clear flag, clear timer, and persist state.
function stopEncryption() {
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
  if (message.action === "startEncryption") {
    startEncryption();
  } else if (message.action === "stopEncryption") {
    stopEncryption();
  }
});
