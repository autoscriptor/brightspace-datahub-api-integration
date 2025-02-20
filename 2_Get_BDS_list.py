import requests
import json
import csv

# ----------------------
# Step 1: Load the Refresh Token
# ----------------------

# Load the refresh token from the file where it was stored
with open('refresh_token.txt', 'r') as f:
    refresh_token = f.read().strip()

# Client credentials
client_id = "your-client-id"
client_secret = "your-client-secret"
token_url = "https://auth.brightspace.com/core/connect/token"

# ----------------------
# Step 2: Request New Access Token Using Refresh Token
# ----------------------
data = {
    "grant_type": "refresh_token",  # Using the refresh token grant type
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token
}

# Make a POST request to the token URL
token_response = requests.post(token_url, data=data)

# Check if the token request was successful
if token_response.status_code == 200:
    access_token = token_response.json().get("access_token")
    new_refresh_token = token_response.json().get("refresh_token")
    print("New access token generated:", access_token)

    # ----------------------
    # Step 3: Save the New Refresh Token (if it was updated)
    # ----------------------
    with open('refresh_token.txt', 'w') as f:
        f.write(new_refresh_token)
        print("New refresh token saved.")

    # ----------------------
    # Step 4: Use the Access Token to Make an API Request
    # ----------------------
    api_url = "https://(brightspace.server)/d2l/api/lp/1.47/datasets/bds"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Send a GET request to the Brightspace API
    api_response = requests.get(api_url, headers=headers)

    if api_response.status_code == 200:
        data = api_response.json()
        print("API Response:", data)

        # ----------------------
        # Step 5: Save API Data to JSON File
        # ----------------------
        with open('api_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("Data saved to api_data.json")

    else:
        print(f"Failed to fetch API data: {api_response.status_code} - {api_response.text}")

else:
    print(f"Failed to refresh token: {token_response.status_code} - {token_response.text}")

## Converting JSON to CSV
# Step 1: Load the JSON data from the file
with open('api_data.json', 'r') as json_file:
    json_data = json.load(json_file)

# Step 2: Open a new CSV file for writing
with open('api_data.csv', 'w', newline='') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)

    # Check if json_data has the "Objects" key which is a list
    if "Objects" in json_data and isinstance(json_data["Objects"], list):
        objects_list = json_data["Objects"]

        # Step 3: Write the header
        header = [
            "SchemaId", "ExtractsLink",
            "Full-PluginId", "Full-Name", "Full-Description", "Full-ExtractsLink",
            "Differential-PluginId", "Differential-Name", "Differential-Description", "Differential-ExtractsLink"
        ]
        csv_writer.writerow(header)

        # Step 4: Write the rows (values of each dictionary in JSON data)
        for item in objects_list:
            row = [
                item.get("SchemaId"),
                item.get("ExtractsLink"),
                item.get("Full", {}).get("PluginId"),
                item.get("Full", {}).get("Name"),
                item.get("Full", {}).get("Description"),
                item.get("Full", {}).get("ExtractsLink"),
                item.get("Differential", {}).get("PluginId"),
                item.get("Differential", {}).get("Name"),
                item.get("Differential", {}).get("Description"),
                item.get("Differential", {}).get("ExtractsLink")
            ]
            csv_writer.writerow(row)

    else:
        print("Unsupported JSON format")

print("JSON data successfully cleaned and converted to CSV.")
