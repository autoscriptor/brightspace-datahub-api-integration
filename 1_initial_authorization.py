import urllib.request
import webbrowser
import urllib.parse
import time
import requests

# ----------------------
# Step 1: Redirect to Brightspace Authorization URL
# ----------------------
auth_url = "https://auth.brightspace.com/oauth2/auth"
client_id = "your-client-id"
client_secret = "your-client-secret"
redirect_uri = "https://<callbackserver>/callback.php"  # Set this as your valid redirect URL
scopes = "data:*:* datasets:*:* reporting:*:*"
auth_code_url = "(URL where you stored the authorization code)"

# Build the authorization URL
authorization_url = (
    f"{auth_url}?response_type=code&client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={urllib.parse.quote(scopes)}"
)

# Open the URL in the browser for the user to log in and authorize
print("Redirecting to:", authorization_url)
webbrowser.open(authorization_url)

# ----------------------
# Step 2: Wait for Authorization Code to be Stored
# ----------------------
# Wait for a sufficient amount of time to ensure the user completes the authentication
time.sleep(10)  # Adjust this if needed, depending on network speed or user interaction

# ----------------------
# Step 3: Retrieve Authorization Code from HTML file using urllib
# ----------------------
# We spoof the User-Agent to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

req = urllib.request.Request(auth_code_url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        authorization_code = response.read().decode('utf-8').strip()  # Read the file contents and strip any newlines
        if authorization_code:
            print(f"Authorization code retrieved: {authorization_code}")
        else:
            print("Authorization code is empty. Please ensure the file contains the correct code.")
            exit(1)
except urllib.error.URLError as e:
    print(f"Failed to retrieve authorization code. Reason: {e}")
    exit(1)

# ----------------------
# Step 4: Exchange Authorization Code for Access Token
# ----------------------
token_url = "https://auth.brightspace.com/core/connect/token"

# Data to send to the token endpoint
data = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "code": authorization_code,
}

# Requesting the token
token_response = requests.post(token_url, data=data)

# Check if the token request was successful
if token_response.status_code == 200:
    token = token_response.json().get("access_token")
    refresh_token = token_response.json().get("refresh_token")
    print("Access token generated:", token)
    print("Refresh token generated:", refresh_token)

    # Store the refresh token for future use
    with open('refresh_token.txt', 'w') as f:
        f.write(refresh_token)

    # ----------------------
    # Step 5: Use the Access Token to Make an API Request
    # ----------------------
    api_url = "(brightspace.server)/d2l/api/lp/1.47/dataExport/list"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send a GET request to the Brightspace API
    api_response = requests.get(api_url, headers=headers)

    if api_response.status_code == 200:
        print("API Response:", api_response.json())
    else:
        print(f"Failed to fetch API data: {api_response.status_code} - {api_response.text}")

else:
    print(f"Failed to generate token: {token_response.status_code} - {token_response.text}")
