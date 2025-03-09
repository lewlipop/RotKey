<!DOCTYPE html>
<html>
<!-- Registration Page -->
<head>
    <title>Register</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/main.css">
    <script type="text/javascript" src="/js/checkStatus.js"></script>
    <script type="text/javascript" src="/js/regValidate.js"></script>
</head>

<body>
    <!-- Navigation bar -->
    <?php
    include "./navbar.php";
    ?>

    <div class="flex-container">
        <!-- Register Form -->
        <form id="registerForm">
            <fieldset>
                <legend><b>Register Form</b></legend>
                <p class="note">Please fill out <b>all</b> fields to complete your registration.</p>

                <label for="femail"><b class="form-error">*</b>Email:</label><br>
                <input type="email" id="femail" name="femail" class="text-input" required><br>
                <p class="form-error" id="femailError"></p>

                <label for="fname"><b class="form-error">*</b>Username:</label><br>
                <input type="text" id="fname" name="fname" class="text-input" required><br>
                <p class="form-error" id="fnameError"></p><br>

                <h4 class="note"><u>Note</u></h4>
                <p class="note">Password must be at least 8 characters long.</p>
                <p class="note">Password must contain: Special characters, Numbers, Uppercase and Lowercase letters.</p><br>
                <label for="fpwd"><b class="form-error">*</b>Password:</label><br>
                <input type="password" id="fpwd" name="fpwd" class="text-input" minlength="8" required><br>
                <p class="form-error" id="fpwdError"></p>

                <label for="fconfirmPwd"><b class="form-error">*</b>Confirm Password:</label><br>
                <input type="password" id="fconfirmPwd" name="fconfirmPwd" class="text-input" minlength="8" required><br>
                <p class="form-error" id="fconfirmPwdError"></p>

                <p>By registering, you accept <a href="https://gist.github.com/MattIPv4/045239bc27b16b2bcf7a3a9a4648c08a" target="_blank">
                    the Terms of Use and Privacy Policy</a> mentioned in this link.</p>

                <input type="submit" value="Register" class="form-submit" id="fsubmit">
                <hr>

                <!-- Link to login page -->
                <p>Already have an account? Click <a href="./login.php">here</a> to login.</p>
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

        document.getElementById("registerForm").addEventListener("submit", function(event) {
            event.preventDefault(); // Prevent form submission

            // Obtain submitted values from the Register Page
            const email = document.getElementById("femail").value;
            const username = document.getElementById("fname").value;
            const password = document.getElementById("fpwd").value;
            const data = {
                email: email,
                username: username,
                password: password
            };

            console.log("Sending Data:", data);
            // Using async/await for better error handling and readability
            async function register() {
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
                        const registerResponse = await fetch('/process_register', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });

                        const registerData = await registerResponse.json();
                        console.log("Register response:", registerData);

                        if (!registerResponse.ok) {
                            throw new Error(registerData.message || 'Registration failed'); // Throw an error if registration fails
                        }

                        // Display success message and then redirect to login.php
                        alert(registerData.message);
                        window.location.href = './login.php';

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
                    const registerResponse = await fetch('/process_register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            encryptedData: ciphertextArray,
                            iv: Array.from(iv)
                        })
                    });

                    const registerData = await registerResponse.json();
                    console.log("Register response:", registerData);

                    if (!registerResponse.ok) {
                        throw new Error(registerData.message || 'Registration failed'); // Throw an error if registration fails
                    }

                    // Display success message and then redirect to login.php
                    alert(registerData.message);
                    window.location.href = './login.php';

                } catch (error) {
                    // Handle the error and display it to the user
                    console.error('Error:', error);
                    alert(`Error: ${error.message}`); // Show an alert to the user
                }
            }

            register();

        });
    </script>

</body>

</html>
