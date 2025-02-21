document.addEventListener("DOMContentLoaded", () => {
  console.log("Popup loaded.");
  const statusLabel = document.getElementById("status");
  const countdownDisplay = document.getElementById("countdownDisplay");
  const keyDisplay = document.getElementById("keyDisplay");
  const compatibilityStatus = document.getElementById("compatibilityStatus");
  const startButton = document.getElementById("start");
  const stopButton = document.getElementById("stop");
  const rotationInterval = 300; // seconds (5 minutes)
  let countdownTimer;

  // Fixed server URL
  const serverUrl = "https://192.168.86.30:5000";

  // Check handshake with the server to verify compatibility.
  async function checkHandshake() {
    console.log("Performing handshake with", serverUrl + "/rotkey-handshake");
    try {
      const response = await fetch(`${serverUrl}/rotkey-handshake`, {
        method: "GET",
        mode: "cors"
      });
      if (!response.ok) throw new Error("Non-200 response");
      const data = await response.json();
      console.log("Handshake response:", data);
      if (data.status === "ok") {
        compatibilityStatus.textContent = "Compatible: Yes";
        compatibilityStatus.style.color = "#4CAF50";
      } else {
        compatibilityStatus.textContent = "Compatible: No";
        compatibilityStatus.style.color = "#f44336";
      }
    } catch (e) {
      console.error("Handshake error:", e);
      compatibilityStatus.textContent = "Compatible: No";
      compatibilityStatus.style.color = "#f44336";
    }
  }

  // Start handshake on popup load.
  checkHandshake();

  function updateCountdownDisplay(timeLeft) {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    countdownDisplay.textContent = `Next key rotation in: ${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    console.log("Countdown updated:", minutes, seconds);
  }

  function startCountdown(initialTimeLeft) {
    let timeLeft = Math.floor(initialTimeLeft);
    console.log("Starting countdown with", timeLeft, "seconds left.");
    updateCountdownDisplay(timeLeft);
    if (countdownTimer) clearInterval(countdownTimer);
    countdownTimer = setInterval(() => {
      timeLeft--;
      if (timeLeft < 0) timeLeft = rotationInterval;
      updateCountdownDisplay(timeLeft);
    }, 1000);
  }

  function stopCountdown() {
    console.log("Stopping countdown.");
    clearInterval(countdownTimer);
    countdownDisplay.textContent = "Key rotation stopped";
  }

  chrome.storage.local.get(["encryptionEnabled", "lastRotation", "sharedKey"], (data) => {
    console.log("Restored state in popup:", data);
    if (data.encryptionEnabled) {
      statusLabel.textContent = "Active";
      statusLabel.style.color = "#4CAF50";
      keyDisplay.textContent = data.sharedKey ? "Current Key: " + data.sharedKey : "Current Key: Not available";
      const lastRotation = data.lastRotation || Date.now();
      const elapsed = Math.floor((Date.now() - lastRotation) / 1000);
      let timeLeft = rotationInterval - elapsed;
      if (timeLeft < 0) timeLeft = rotationInterval;
      startCountdown(timeLeft);
    } else {
      statusLabel.textContent = "Inactive";
      statusLabel.style.color = "#f44336";
      countdownDisplay.textContent = "Key rotation stopped";
      keyDisplay.textContent = "Current Key: N/A";
    }
  });

  startButton.addEventListener("click", () => {
    console.log("Start button clicked.");
    chrome.runtime.sendMessage({ action: "startEncryption" }, () => {
      console.log("Sent startEncryption message.");
    });
    statusLabel.textContent = "Active";
    statusLabel.style.color = "#4CAF50";
    startCountdown(rotationInterval);
    setTimeout(() => {
      chrome.storage.local.get("sharedKey", (data) => {
        console.log("Shared key from storage:", data.sharedKey);
        if (data.sharedKey) {
          keyDisplay.textContent = "Current Key: " + data.sharedKey;
        }
      });
    }, 2000);
    // Re-check compatibility after starting encryption.
    checkHandshake();
  });

  stopButton.addEventListener("click", () => {
    console.log("Stop button clicked.");
    chrome.runtime.sendMessage({ action: "stopEncryption" }, () => {
      console.log("Sent stopEncryption message.");
    });
    statusLabel.textContent = "Inactive";
    statusLabel.style.color = "#f44336";
    stopCountdown();
    keyDisplay.textContent = "Current Key: N/A";
    compatibilityStatus.textContent = "Compatible: N/A";
    compatibilityStatus.style.color = "#f44336";
  });
});
