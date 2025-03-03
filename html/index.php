<?php
//session_start();  // Start the session to check if the user is logged in

//echo '<pre>';
//print_r($_SESSION);  // Displays all session variables
//echo '</pre>';

//
?>

<html>

<head>
    <title>A Normal Website</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/main.css">
    <script type="text/javascript" src="/js/checkStatus.js"></script>
</head>

<body>
    <!-- Navigation bar -->
    <?php
    include "./navbar.php";
    ?>



    <?php if (isset($_SESSION['username'])): ?>
        <!-- <?php echo 'Logged in as: ' . $_SESSION['username'] ?>; -->
        <!-- If user logged in, show this content -->
        <div class="flex-container">
            <div class="flex-card">
                <h1><u>Welcome to my Website, <?php echo htmlspecialchars($_SESSION['username']); ?>!</u></h1>
                <p>You have successfully logged in! You can see this masterpiece now.</p>
            </div>

            <div class="flex-card">
                <img src="/images/kawaii.png" alt="Kawaii Image">
            </div>
        </div>
    <?php else: ?>
        <!-- <?php echo 'No user is logged in.' ?>; -->
        <!-- If user not logged in, show this content -->
        <div class="flex-container">
            <div class="flex-card">
                <h1><u>Welcome to my Website</u></h1>
                <p>Login to see more stuff.</p>
            </div>
        </div>
    <?php endif; ?>

</body>

</html>
