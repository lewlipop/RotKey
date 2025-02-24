<script>

    console.log("Checking started");

    // Function to check if the RotKey extension is installed and key rotation is started
    function checkRotKeyExtension() {
        const extensionId = "agdbicdmcaeneefgkidljbnpgdceakok"; // Replace with new extension ID if not working (Manage extensions > Details )
        console.log("Checking RotKey extension with ID:", extensionId);

        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage(extensionId, { action: "checkKeyRotation" }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Error:", chrome.runtime.lastError.message);
                } else {
                    console.log("Response from extension:", response);
                    if (!response || response.status !== "active") {
                        showPopup();
                    } else {
                        hidePopup();
                    }
                }
            });
        } else {
            console.error("chrome.runtime.sendMessage is not available.");
            showPopup();
        }
    }

        // Function to show the popup
        function showPopup() {
            console.log("Showing popup");
            const popup = document.createElement('div');
            popup.id = 'extension-popup';
            popup.style.position = 'fixed';
            popup.style.top = '0';
            popup.style.left = '0';
            popup.style.width = '100%';
            popup.style.height = '100%';
            popup.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            popup.style.color = 'white';
            popup.style.display = 'flex';
            popup.style.flexDirection = 'column';
            popup.style.justifyContent = 'center';
            popup.style.alignItems = 'center';
            popup.style.zIndex = '1000';

            const message = document.createElement('p');
            message.textContent = 'Please enable the RotKey extension to continue.';
            message.style.fontSize = '24px';
            message.style.textAlign = 'center';

            const button = document.createElement('button');
            button.textContent = 'Check Again';
            button.style.marginTop = '20px';
            button.style.padding = '10px 20px';
            button.style.fontSize = '18px';
            button.onclick = () => {
                checkRotKeyExtension();
            };

            popup.appendChild(message);
            popup.appendChild(button);
            document.body.appendChild(popup);
        }

        // Function to hide the popup
        function hidePopup() {
            console.log("Hiding popup");
            const popup = document.getElementById('extension-popup');
            if (popup) {
                popup.remove();
            }
        }
    // Call the function to check the RotKey extension status
    checkRotKeyExtension();
</script>

