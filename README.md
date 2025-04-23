# brightspace-datahub-api-integration
Small application to extract Brightspace standard and advanced Data Hub files  

# Brightspace API Integration

This project automates the retrieval of data from the Brightspace API, including authentication and dataset downloads.

## Features
- OAuth2 Authentication
- Downloading and extracting Brightspace datasets
- Handling API calls efficiently

## Steps
1. Create your own OAuth 2.0 app on Brightspace
2. You will need a web server to run the callback.php file. The webserver should have access to the internet
3. Review all the Python scripts in this github and replace placeholders with your own values
4. Run the script (1) -Runs one time only or whenever you need a new authorization code
5. Run script (2) to create the file api_data.csv which is a list of all Brightsapce Datasets, their Schema IDs, and their difinitions downloadn location. -Runs once time only
6. STOP HERE and take some time and create your own SchemaId_Lookup.csv file. Contains one coulmn that has the SchemaIDs of the datasets you want to download. The file shoudl have the header "SchemaId"
7. Schedule to run the scripts (3) and (4) 
