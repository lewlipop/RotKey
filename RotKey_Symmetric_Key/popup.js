document.addEventListener("DOMContentLoaded", () => {
    console.log("Popup loaded.");
    const statusLabel = document.getElementById("status");
    const countdownDisplay = document.getElementById("countdownDisplay");
    const keyDisplay = document.getElementById("keyDisplay");
    const startButton = document.getElementById("start");
    const stopButton = document.getElementById("stop");
    const rotationInterval = 300; // seconds (5 minutes)
    let countdownTimer;
  
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
    });
  });
  