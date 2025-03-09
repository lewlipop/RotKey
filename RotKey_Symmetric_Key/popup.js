// Wait until the DOM is fully loaded before executing the script
document.addEventListener("DOMContentLoaded", () => {
    console.log("Popup loaded.");
    const statusLabel = document.getElementById("status");
    const countdownDisplay = document.getElementById("countdownDisplay");
    const keyDisplay = document.getElementById("keyDisplay");
    const startButton = document.getElementById("start");
    const stopButton = document.getElementById("stop");
    const rotationInterval = 300; // Define the key rotation interval in seconds (5 minutes)
    let countdownTimer;
  
    // Function to update the countdown display in the UI
    function updateCountdownDisplay(timeLeft) {
      const minutes = Math.floor(timeLeft / 60);
      const seconds = timeLeft % 60;
      countdownDisplay.textContent = `Next key rotation in: ${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
      console.log("Countdown updated:", minutes, seconds);
    }
  
    // Function to start the countdown timer using an initial time left value
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
  
    // Function to stop the countdown timer and update the UI accordingly
    function stopCountdown() {
      console.log("Stopping countdown.");
      clearInterval(countdownTimer);
      countdownDisplay.textContent = "Key rotation stopped";
    }
  
    // Retrieve stored state from chrome.storage when the popup loads
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
  
    // Event listener for the Start button
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
  
    // Event listener for the Stop button
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
  
