<!-- Codes for Navigation Bar -->
<div id="navbar">
    <?php
    session_start(); // Start the session to check if the user is logged in

    if (!isset($_SESSION['username'])): ?>
        <!-- If user is not logged in, show login button -->
        <a href="./login.php"><button class="navbar-butt">Login</button></a>

        <button id="checkRotKeyStatus" class="navbar-butt">Check RotKey Status</button>
    
    <?php else: ?>
        <!-- If user is logged in, replace login button with Log Out button -->
        <a href="./logout.php"><button class="navbar-butt">Log Out</button></a>
    <?php endif; ?>

    <a href="./index.php"><button class="navbar-butt">Home</button></a>
    
</div>
