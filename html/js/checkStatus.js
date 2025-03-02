document.addEventListener("DOMContentLoaded", function() {
  const checkRotKeyStatusButton = document.getElementById("checkRotKeyStatus");
  if (checkRotKeyStatusButton) {
    checkRotKeyStatusButton.addEventListener("click", async function() {
      try {
        // Replace 'your-extension-id' with your actual extension ID
        const extensionId = 'agdbicdmcaeneefgkidljbnpgdceakok';
        
        // Check RotKey status
        const response = await new Promise((resolve, reject) => {
          chrome.runtime.sendMessage(extensionId, { action: "checkKeyRotation" }, (response) => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve(response);
            }
          });
        });

        if (response.status === "active") {
          // RotKey is active, request background script to update the key
          chrome.runtime.sendMessage(extensionId, { action: "updateKey" }, (response) => {
            console.log("Update key response:", response);
            alert("RotKey Synced!");
          });
        } else {
          // RotKey is inactive, request background script to delete the key
          chrome.runtime.sendMessage(extensionId, { action: "deleteKey" }, (response) => {
            console.log("Delete key response:", response);
            alert("RotKey is Not Enabled Yet!");
          });
        }
      } catch (error) {
        console.error("Error checking RotKey status:", error);
      }
    });
  } else {
    console.error("Button with ID 'checkRotKeyStatus' not found.");
  }
});
