<html>
    <head>
        <title>Register</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/css/main.css">
        <script type="text/javascript" src="/js/regValidate.js"></script>
    </head>

    <body>
        <!-- Navigation bar -->
        <?php
            include "./navbar.php";
            //include "./prompt_extension.php"
        ?>

        <div class="flex-container">
            <!-- Register Form -->
            <form method="POST" id="registerForm">
                <fieldset>
                    <legend><b>Register Form</b></legend>
                    <p class="note">Please fill out <b>all</b> fields to complete your registration.</p>

                    <label for="femail"><b class="form-error">*</b>Email:</label><br>
                    <input type="email" id="femail" name="femail" class="text-input" required></input><br>
                    <p class="form-error" id="femailError"></p>

                    <label for="fname"><b class="form-error">*</b>Username:</label><br>
                    <input type="text" id="fname" name="fname" class="text-input" required></input><br>
                    <p class="form-error" id="fnameError"></p><br>

                    <h4 class="note"><u>Note</u></h4>
                    <p class="note">Password must be at least 8 characters long.</p>
                    <p class="note">Password must contain: Special characters, Numbers, Uppercase and Lowercase letters.</p><br>
                    <label for="fpwd"><b class="form-error">*</b>Password:</label><br>
                    <input type="password" id="fpwd" name="fpwd" class="text-input" minlength="8" required></input><br>
                    <p class="form-error" id="fpwdError"></p>

                    <label for="fconfirmPwd"><b class="form-error">*</b>Confirm Password:</label><br>
                    <input type="password" id="fconfirmPwd" name="fconfirmPwd" class="text-input" minlength="8" required></input><br>
                    <p class="form-error" id="fconfirmPwdError"></p>

		    <p>By regisering, you accept <a href="https://gist.github.com/MattIPv4/045239bc27b16b2bcf7a3a9a4648c08a" target="_blank">
                    the Terms of Use and Privacy Policy</a> mentioned in this link.</p>

                    <input type="button" value="Register" class="form-submit" id="fsubmit" onclick="register()"></input>
                    <hr>

                    <!-- Link to login page -->
                    <p>Already have an account? Click <a href="./login.php">here</a> to login.</p>
                </fieldset>
            </form>
        </div>

        <script>
            // Submit the form data if validation passes
            function register() {
                if (validateForm()) {
                    // Get values from the form
                    const email = document.getElementById("femail").value;
                    const username = document.getElementById("fname").value;
                    const password = document.getElementById("fpwd").value;

                    // Create a data object to send in the request body
                    const data = {
                        email: email,
                        username: username,
                        password: password
                    };

                    console.log("Sending Data:", data);

                    // Send the POST request to Flask backend
                    fetch('/process_register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.success) {
                            alert('Registration successful');
                            // Redirect or show success message
                            window.location.href = 'login.php';  // Redirect to login page
                        } else {
                            alert('Error: ' + result.message);
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
            }
        </script>

    </body>
</html>
