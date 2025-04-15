<?php
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
