<html>
    <head>
        <title>Login</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="./main.css">
    </head>
    <body>
        <!-- Navigation bar -->
        <?php
            include "./navbar.php";
        ?>

        <div class="flex-container">
            <!-- Login Form -->
            <form method="POST" action="." id="loginForm">
                <fieldset>
                    <legend><b>Login Form</b></legend>

                    <label for="fname">Username:</label><br>
                    <input type="text" id="fname" class="text-input" required></input><br>

                    <label for="fpwd">Password:</label><br>
                    <input type="password" id="fpwd" class="text-input" required></input><br>

                    <input type="checkbox" id="frmb">
                    <label for="frmb"> Remember me</label><br>
                    
                    <input type="submit" value="Login" class="form-submit" id="fsubmit"></input>
                    <hr>
                    <p>Don't have an account? Click <a href="./register.php">here</a> to register.</p>
                </fieldset>
            </form>
        </div>
    </body>
</html>