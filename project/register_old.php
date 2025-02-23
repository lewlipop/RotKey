<html>
    <head>
        <title>Register</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="./main.css">
    </head>
    <body>
        <!-- Navigation bar -->
        <?php
            include "./navbar.php";
        ?>

        <!-- Register Javascript -->
        <?php 
            include "./jregister.php";
        ?>

        <div class="flex-container">
            <!-- Register Form -->
            <form method="POST" action="." id="registerForm">
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

                    <input type="checkbox" id="fterms" name="fterms" required>
                    <label for="fterms"> <b class="form-error">*</b>I accept <a href="https://gist.github.com/MattIPv4/045239bc27b16b2bcf7a3a9a4648c08a" target="_blank">Terms of Use and Privacy Policy</a>.</label><br>
                    
                    <input type="button" value="Register" class="form-submit" id="fsubmit" onclick="register()"></input>
                    <hr>

                    <!-- Link to login page -->
                    <p>Already have an account? Click <a href="./login.php">here</a> to login.</p>
                </fieldset>
            </form>
        </div>
    </body>
</html>