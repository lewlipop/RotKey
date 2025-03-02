<html>

<head>
    <title>Login</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/main.css">
</head>

<body>
    <!-- Navigation bar -->
    <?php
    include "./navbar.php";
    
    ?>

    <div class="flex-container">
        <!-- Login Form -->
        <form id="loginForm">
            <fieldset>
                <legend><b>Login Form</b></legend>

                <label for="femail">Email:</label><br>
                <input type="email" id="femail" name="femail" class="text-input" required><br>

                <label for="fpwd">Password:</label><br>
                <input type="password" id="fpwd" name="fpwd" class="text-input" required><br>

                <input type="submit" value="Login" class="form-submit" id="fsubmit">
                <hr>
                <p>Don't have an account? Click <a href="./register.php">here</a> to register.</p>
            </fieldset>
        </form>
    </div>

    <script>
        function hexToArrayBuffer(hex) {
            const typedArray = new Uint8Array(hex.match(/[\da-f]{2}/gi).map(h => parseInt(h, 16)));
            return typedArray.buffer;
        }

        async function importKeyFromHex(hex) {
            const keyBuffer = hexToArrayBuffer(hex);
            return await window.crypto.subtle.importKey(
                "raw",
                keyBuffer, {
                    name: "AES-GCM"
                },
                false,
                ["encrypt", "decrypt"]
            );
        }

        async function encryptWithKey(plaintext, key, iv) {
            const encoder = new TextEncoder();
            const encoded = encoder.encode(plaintext);
            return await window.crypto.subtle.encrypt({
                    name: "AES-GCM",
                    iv: iv
                },
                key,
                encoded
            );
        }

        function fetchSharedKey() {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open("GET", "/get-shared-key", true);
                xhr.setRequestHeader("Content-Type", "application/json");

                xhr.onreadystatechange = function() {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            const data = JSON.parse(xhr.responseText);
                            console.log("SharedKeyHex", data.sharedKey); // Debug the response
                            resolve(data.sharedKey);
                        } else {
                            reject(new Error("Failed to fetch shared key"));
                        }
                    }
                };

                xhr.send();
            });
        }

        document.getElementById("loginForm").addEventListener("submit", function(event) {
            event.preventDefault(); // Prevent form submission

            const email = document.getElementById("femail").value;
            const password = document.getElementById("fpwd").value;
            const data = {
                email: email,
                password: password
            };

            console.log("Sending Data:", data);
            // Using async/await for better error handling and readability
            async function login() {
                const iv = crypto.getRandomValues(new Uint8Array(12));
                let sharedKeyHex;
                try {
                    sharedKeyHex = await fetchSharedKey();
                } catch (error) {
                    console.error("Failed to fetch shared key:", error);
                }

                if (!sharedKeyHex) {
                    console.warn("Shared key not available. Sending data without encryption.");
                    try {
                        const loginResponse = await fetch('/process_login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });

                        const loginData = await loginResponse.json();
                        console.log("Login response:", loginData);

                        if (!loginResponse.ok) {
                            throw new Error(loginData.message || 'Login failed'); // Throw an error if login fails
                        }

                        // If login is successful, set session in PHP and redirect to index.php
                        const sessionResponse = await fetch('./set_session.php', {
                            method: 'POST',
                            body: JSON.stringify({
                                username: loginData.username
                            }), // Assuming the username is returned by Flask
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });

                        if (!sessionResponse.ok) {
                            throw new Error('Failed to set session');
                        }

                        // After setting the session, redirect to index.php
                        window.location.href = './index.php';

                    } catch (error) {
                        // Handle the error and display it to the user
                        console.error('Error:', error);
                        alert(`Error: ${error.message}`); // Show an alert to the user
                    }
                    return;
                }

                let cryptoKey;
                try {
                    cryptoKey = await importKeyFromHex(sharedKeyHex);
                } catch (err) {
                    alert("Error importing key: " + err);
                    return;
                }
                let ciphertextBuffer;
                try {
                    ciphertextBuffer = await encryptWithKey(JSON.stringify(data), cryptoKey, iv);
                } catch (err) {
                    alert("Encryption error: " + err);
                    return;
                }
                try {
                    const ciphertextArray = Array.from(new Uint8Array(ciphertextBuffer));
                    console.log("Encrypted data:", ciphertextArray);
                    const loginResponse = await fetch('/process_login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            encryptedData: ciphertextArray,
                            iv: Array.from(iv)
                        })
                    });

                    const loginData = await loginResponse.json();
                    console.log("Login response:", loginData);

                    if (!loginResponse.ok) {
                        throw new Error(loginData.message || 'Login failed'); // Throw an error if login fails
                    }

                    // If login is successful, set session in PHP and redirect to index.php
                    const sessionResponse = await fetch('./set_session.php', {
                        method: 'POST',
                        body: JSON.stringify({
                            username: loginData.username
                        }), // Assuming the username is returned by Flask
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!sessionResponse.ok) {
                        throw new Error('Failed to set session');
                    }

                    // After setting the session, redirect to index.php
                    window.location.href = './index.php';

                } catch (error) {
                    // Handle the error and display it to the user
                    console.error('Error:', error);
                    alert(`Error: ${error.message}`); // Show an alert to the user
                }
            }

            login();

        });
    </script>

</body>

</html>