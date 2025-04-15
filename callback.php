<?php
/*
This is your callback script. The URL for this file should be your redirect URI. 
This script should receive the authorization code and be securely stored so you can exchange it for an access token. 
The process of exchanging the authorization code for an access token is already part of the file 1_initail_authorzation.py
*/
if (isset($_GET['code'])) {
    $auth_code = $_GET['code'];

    // Create a simple HTML file to store just the authorization code
    $file = 'auth_code.html';
    
    // The HTML content only contains the authorization code, no extra tags
    $html_content = $auth_code;
    
    // Write the authorization code to the HTML file
    file_put_contents($file, $html_content);
    
    echo "Authorization Code stored successfully in auth_code.html.";
} else {
    echo "Authorization code not found.";
}
?>
