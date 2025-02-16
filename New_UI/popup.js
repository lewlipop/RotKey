document.addEventListener("DOMContentLoaded", () => {
  const statusLabel = document.getElementById("status");
  const countdownDisplay = document.getElementById("countdownDisplay");
  const keyDisplay = document.getElementById("keyDisplay");
  const startButton = document.getElementById("start");
  const stopButton = document.getElementById("stop");
  const rotationInterval = 300; // seconds (5 minutes)
  let countdownTimer;

  // Function to update the countdown display.
  function updateCountdownDisplay(timeLeft) {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    countdownDisplay.textContent = `Next key rotation in: ${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }

  // Start the local countdown timer with initial timeLeft.
  function startCountdown(initialTimeLeft) {
    let timeLeft = Math.floor(initialTimeLeft);
    updateCountdownDisplay(timeLeft);
    if (countdownTimer) clearInterval(countdownTimer);
    countdownTimer = setInterval(() => {
      timeLeft--;
      if (timeLeft < 0) {
        timeLeft = rotationInterval;
      }
      updateCountdownDisplay(timeLeft);
    }, 1000);
  }

  // Stop the countdown timer.
  function stopCountdown() {
    clearInterval(countdownTimer);
    countdownDisplay.textContent = "Key rotation stopped";
  }

  // Restore state when popup loads.
  chrome.storage.local.get(["encryptionEnabled", "lastRotation", "sharedKey"], (data) => {
    console.log("Restored state:", data);
    if (data.encryptionEnabled) {
      statusLabel.textContent = "Active";
      // Display the current key (for demo purposes, show the full key or a masked version).
      if (data.sharedKey) {
        keyDisplay.textContent = "Current Key: " + data.sharedKey;
      } else {
        keyDisplay.textContent = "Current Key: Not available";
      }
      // Calculate elapsed time (in seconds) since the last rotation.
      const lastRotation = data.lastRotation || Date.now();
      const elapsed = Math.floor((Date.now() - lastRotation) / 1000);
      let timeLeft = rotationInterval - elapsed;
      if (timeLeft < 0) timeLeft = rotationInterval;
      startCountdown(timeLeft);
    } else {
      statusLabel.textContent = "Inactive";
      countdownDisplay.textContent = "Key rotation stopped";
      keyDisplay.textContent = "Current Key: N/A";
    }
  });

  // Listen for Start button click.
  startButton.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "startEncryption" });
    statusLabel.textContent = "Active";
    startCountdown(rotationInterval);
    // Optionally, update the key display after a short delay to allow the background to perform key exchange.
    setTimeout(() => {
      chrome.storage.local.get("sharedKey", (data) => {
        if (data.sharedKey) {
          keyDisplay.textContent = "Current Key: " + data.sharedKey;
        }
      });
    }, 2000);
  });

  // Listen for Stop button click.
  stopButton.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "stopEncryption" });
    statusLabel.textContent = "Inactive";
    stopCountdown();
    keyDisplay.textContent = "Current Key: N/A";
  });
});
