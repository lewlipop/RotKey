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
            <form method="POST" action="https://127.0.0.1:5000/process_login" id="loginForm">
                <fieldset>
                    <legend><b>Login Form</b></legend>

                    <label for="fname">Username:</label><br>
                    <input type="text" id="fname" name="fname" class="text-input" required><br>

                    <label for="fpwd">Password:</label><br>
                    <input type="password" id="fpwd" name="fpwd" class="text-input" required><br>

                    <input type="checkbox" id="frmb" name="frmb">
                    <label for="frmb"> Remember me</label><br>
                    
                    <input type="submit" value="Login" class="form-submit" id="fsubmit">
                    <hr>
                    <p>Don't have an account? Click <a href="./register.php">here</a> to register.</p>
                </fieldset>
            </form>
        </div>
    </body>
</html>
