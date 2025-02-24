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
    //include "./prompt_extension.php"
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
                try {
                    const loginResponse = await fetch('/process_login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const loginData = await loginResponse.json();
                    console.log(loginData)

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
