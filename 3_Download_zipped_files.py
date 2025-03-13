import requests
import json
import csv
import os
import zipfile

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
    # Step 4: Load Extract URLs from CSV and Make API Requests
    # ----------------------
    with open('api_data.csv', 'r') as csv_file, open('SchemaId_Lookup.csv', 'r') as lookup_file:
        csv_reader = csv.DictReader(csv_file)
        lookup_reader = csv.DictReader(lookup_file)
        lookup_schema_ids = {row['SchemaId'] for row in lookup_reader}
        json_results = []

        for row in csv_reader:
            if row['SchemaId'] in lookup_schema_ids:
                extract_url = row['Full-ExtractsLink']
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                # Send a GET request to the Brightspace API
                api_response = requests.get(extract_url, headers=headers)

                if api_response.status_code == 200:
                    data = api_response.json()
                    json_results.append(data)
                    print(f"Data fetched successfully from {extract_url}")
                else:
                    print(f"Failed to fetch API data from {extract_url}: {api_response.status_code} - {api_response.text}")

    # ----------------------
    # Step 5: Save All API Data to a Single JSON File
    # ----------------------
    with open('api_data_combined.json', 'w') as json_file:
        json.dump(json_results, json_file, indent=4)
    print("All data saved to api_data_combined.json")

    # ----------------------
    # Step 6: Download Only the Most Recent File per SchemaId
    # ----------------------
    downloads_dir = "Downloads"
    os.makedirs(downloads_dir, exist_ok=True)

    # Dictionary to store the latest object per SchemaId
    latest_objects = {}

    # Identify the most recent object per SchemaId
    for item in json_results:
        if 'Objects' in item:
            for obj in item['Objects']:
                schema_id = obj["SchemaId"]
                created_date = datetime.strptime(obj["CreatedDate"], "%Y-%m-%dT%H:%M:%S.%fZ")

                # Keep only the latest object per SchemaId
                if schema_id not in latest_objects or created_date > latest_objects[schema_id]["CreatedDate"]:
                    latest_objects[schema_id] = {"CreatedDate": created_date, "Object": obj}

    # Download only the latest extract for each SchemaId
    for schema_id, entry in latest_objects.items():
        obj = entry["Object"]
        download_url = obj["DownloadLink"]
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        download_response = requests.get(download_url, headers=headers, stream=True)

        if download_response.status_code == 200:
            filename = os.path.join(downloads_dir, f"{schema_id}.zip")
            with open(filename, 'wb') as file:
                for chunk in download_response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully: {filename}")
        else:
            print(f"Failed to download file from {download_url}: {download_response.status_code} - {download_response.text}")
    # ----------------------
    # Step 7: Extract Downloaded Files
    # ----------------------
    uncompressed_dir = r"(path to store files)"
    os.makedirs(uncompressed_dir, exist_ok=True)

    for filename in os.listdir(downloads_dir):
        if filename.endswith(".zip"):
            zip_path = os.path.join(downloads_dir, filename)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(uncompressed_dir)
                print(f"Extracted: {zip_path} to {uncompressed_dir}")
            except zipfile.BadZipFile:
                print(f"Failed to extract {zip_path}: Bad zip file")
else:
    print(f"Failed to refresh token: {token_response.status_code} - {token_response.text}")
