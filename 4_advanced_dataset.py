import requests
import json
import time
from datetime import datetime
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
    # Step 4: Get List of Available Advanced Datasets
    # ----------------------
    datasets_url = "https://(yourbrightspace.server))/d2l/api/lp/1.47/dataExport/list"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    datasets_response = requests.get(datasets_url, headers=headers)

    if datasets_response.status_code == 200:
        datasets = datasets_response.json()
        print("Datasets available:", datasets)

        # Save dataset list response for debugging
        with open('datasets_list_response.json', 'w') as f:
            json.dump(datasets, f, indent=4)

        # ----------------------
        # Step 5: Iterate through Selected Datasets and Create Export Jobs
        # ----------------------
        selected_datasets = [
            "Final Grades",
            "Enrollments and Withdrawals",
            "All Grades",
            "Learner Usage",
            "Impersonated Session History",
            "Instructor Usage",
            "Content Progress",
            "Course Offering Enrollments"
        ]

        for dataset in datasets:
            dataset_id = dataset.get("DataSetId")
            dataset_name = dataset.get("Name")
            if dataset_name not in selected_datasets:
                continue

            print(f"Processing dataset: {dataset_name} (ID: {dataset_id})")

            export_job_url = "(yourbrightspace.server)/d2l/api/lp/1.47/dataExport/create"
            start_date = "2025-01-05T00:00:00.000Z"
            end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Prepare the payload with default filters, allowing additional filters if available
            payload = {
                "DataSetId": dataset_id,
                "Filters": []
            }

            # Add common filters
            payload["Filters"].append({"Name": "parentOrgUnitId", "Value": "6863"})
            payload["Filters"].append({"Name": "startDate", "Value": start_date})
            payload["Filters"].append({"Name": "endDate", "Value": end_date})

            # Add additional filters if present in dataset metadata
            for filter_item in dataset.get("Filters", []):
                if filter_item["Name"] == "roles":
                    payload["Filters"].append({"Name": "roles", "Value": "174,362,916,923,172,359"})
                elif filter_item["Name"] not in ["parentOrgUnitId", "startDate", "endDate"]:
                    payload["Filters"].append({"Name": filter_item["Name"], "Value": filter_item.get("DefaultValue", None)})

            # Log the payload for debugging
            print("Payload for dataset:", dataset_name, json.dumps(payload, indent=4))

            export_response = requests.post(export_job_url, headers=headers, json=payload)

            if export_response.status_code == 200 or export_response.status_code == 202:
                export_job_id = export_response.json().get("ExportJobId")
                print("Export job created successfully. Job ID:", export_job_id)

                # ----------------------
                # Step 6: Poll for Export Job Completion
                # ----------------------
                status_url = f"(yourbrightspace.server)/d2l/api/lp/1.47/dataExport/jobs/{export_job_id}"
                job_status = 0

                while job_status != 2:  # Status 2 means the job is complete
                    status_response = requests.get(status_url, headers=headers)
                    if status_response.status_code == 200:
                        job_status = status_response.json().get("Status")
                        print("Current job status:", job_status)
                        if job_status == 2:
                            print("Export job completed successfully.")
                            break
                        elif job_status in [3, 4]:  # Status 3 or 4 indicates a failure
                            print("Export job failed or was canceled.")
                            break
                    else:
                        print(f"Failed to get job status: {status_response.status_code} - {status_response.text}")
                        break
                    time.sleep(10)  # Wait for 10 seconds before polling again

                # ----------------------
                # Step 7: Download the Exported Data
                # ----------------------
                download_url = f"(yourbrightspace.server)/d2l/api/lp/1.47/dataExport/download/{export_job_id}"
                download_response = requests.get(download_url, headers=headers, stream=True)

                if download_response.status_code == 200:
                    downloads_dir = r"Path to save files"
                    uncompressed_dir = r"Path to save files"
                    os.makedirs(downloads_dir, exist_ok=True)
                    os.makedirs(uncompressed_dir, exist_ok=True)

                    zip_file_path = os.path.join(downloads_dir, f"{dataset_name.replace(' ', '_')}.zip")
                    with open(zip_file_path, 'wb') as file:
                        for chunk in download_response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    print(f"Exported data downloaded successfully: {zip_file_path}")

                    # ----------------------
                    # Step 8: Uncompress the Downloaded File
                    # ----------------------
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        for file in zip_ref.namelist():
                            # Extract each file and rename it based on the zip file's name
                            extracted_file_name = f"{os.path.splitext(os.path.basename(zip_file_path))[0]}.csv"
                            extracted_file_path = os.path.join(uncompressed_dir, extracted_file_name)
                            with open(extracted_file_path, 'wb') as extracted_file:
                                extracted_file.write(zip_ref.read(file))
                            print(f"Extracted file saved as: {extracted_file_path}")
                else:
                    print(f"Failed to download export: {download_response.status_code} - {download_response.text}")

            else:
                print(f"Failed to create export job for dataset {dataset_name}: {export_response.status_code} - {export_response.text}")

    else:
        print(f"Failed to retrieve dataset list: {datasets_response.status_code} - {datasets_response.text}")

else:
    print(f"Failed to refresh token: {token_response.status_code} - {token_response.text}")
