<?php
// Start the session
session_start();

// Get the POST data from the request
$data = json_decode(file_get_contents('php://input'), true);

// Check if the username is provided
if (isset($data['username'])) {
    // Set the PHP session variable
    $_SESSION['username'] = $data['username'];

    // Store more information in the session if needed
    echo json_encode(['success' => true]);
} else {
    echo json_encode(['success' => false, 'message' => 'No username provided']);
}
