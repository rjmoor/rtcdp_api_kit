import os
import json
import time
import requests
import logging
import csv
from tqdm import tqdm

# Configure new CREDS file

class AdobeQueryService:
    def __init__(self, credentials_file, environment_name):
        """
        Initialize the MergePolicyAPI instance.

        Args:
            credentials_file (str): Path to the credentials file.
            environment_name (str): Name of the environment to use (e.g., 'Development').
        """
        self.credentials_file = credentials_file
        self.credentials = self.load_credentials()
        self.base_url = self.credentials["base_url"]
        self.api_key = self.credentials["api_key"]
        self.org_id = self.credentials["org_id"]
        self.environment = self.get_environment(environment_name)

    def load_credentials(self):
        """Load API credentials from a JSON file."""
        try:
            with open(self.credentials_file, "r") as file:
                return json.load(file)
        except FileNotFoundError as e:
            logging.error("Credentials file not found: %s", e)
            raise
        except json.JSONDecodeError as e:
            logging.error("Error decoding JSON from credentials file: %s", e)
            raise

    def get_environment(self, environment_name):
        """Retrieve the sandbox information for the specified environment."""
        for env in self.credentials.get("environments", []):
            if env["name"] == environment_name:
                return env
        raise ValueError(f"Environment '{environment_name}' not found in credentials.")

    def refresh_access_token(self):
        """Refresh the access token if it is expired."""
        try:
            token_url = f"{self.credentials['ims_url']}/ims/token/v2"
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.credentials["client_id"],
                "client_secret": self.credentials["client_secret"],
                "scope": " ".join(self.credentials.get("scopes", []))
            }
            response = requests.post(token_url, data=payload)
            print(response)
            if response.status_code == 200:
                new_token = response.json()["access_token"]
                self.credentials["access_token"] = new_token
                with open(self.credentials_file, "w") as file:
                    json.dump(self.credentials, file, indent=4)
                logging.info("Access token refreshed successfully.")
                return new_token
            else:
                logging.error("Failed to refresh access token: %s", response.text)
                response.raise_for_status()
        except Exception as e:
            logging.error("Error refreshing access token: %s", e)
            raise

    def get_access_token(self):
        """Ensure a valid access token is available."""
        access_token = self.credentials.get("access_token")
        if not access_token:
            access_token = self.refresh_access_token()
        return access_token
# =====================================================================================================
   
    # def __init__(self, credentials_path='../CREDS/cit_credentials.json'):
    #     self.credentials_path = credentials_path
    #     self.token_url = "https://ims-na1.adobelogin.com/ims/token/v3"
    #     self.query_service_base_url = "https://platform.adobe.io/data/foundation/query"
    #     self.query_endpoint = f"{self.query_service_base_url}/queries"
    #     self.credentials = self.load_credentials()
    #     self.access_token = self.ensure_valid_token()

    # def load_credentials(self):
    #     required_keys = ["api_key", "client_secret", "org_id", "environments"]
    #     try:
    #         with open(self.credentials_path, 'r') as file:
    #             credentials = json.load(file)
    #             for key in required_keys:
    #                 if key not in credentials:
    #                     raise KeyError(f"Missing required key in credentials.json: {key}")
    #             print("Credentials loaded successfully.")
    #             return credentials
    #     except FileNotFoundError:
    #         print(f"File not found: {self.credentials_path}")
    #         exit()
    #     except json.JSONDecodeError as e:
    #         print(f"Error decoding JSON: {e}")
    #         exit()
    #     except KeyError as e:
    #         print(f"Credential Error: {e}")
    #         exit()

    # def save_credentials(self):
    #     with open(self.credentials_path, 'w') as file:
    #         json.dump(self.credentials, file, indent=4)
    #     print("Updated credentials saved.")

    # def refresh_access_token(self):
    #     payload = {
    #         "grant_type": "client_credentials",
    #         "client_id": self.credentials["AEP_API_KEY"],
    #         "client_secret": self.credentials["client_secret"],
    #         "scope": "openid,AdobeID,read_pc.acp,read_pc,read_pc.dma_tartan,additional_info,read_organizations,additional_info.projectedProductContext,session"
    #     }
    #     response = requests.post(self.token_url, data=payload)
    #     if response.status_code == 200:
    #         token_data = response.json()
    #         new_access_token = token_data.get("access_token")
    #         expires_in = token_data.get("expires_in")
    #         self.credentials["AEP_ACCESS_TOKEN"] = new_access_token
    #         self.credentials["AEP_TOKEN_EXPIRY"] = time.time() + expires_in
    #         self.save_credentials()
    #         print("Access token refreshed successfully.")
    #         return new_access_token
    #     else:
    #         print(f"Failed to retrieve access token: {response.status_code}")
    #         print(response.text)
    #         exit()

    # def ensure_valid_token(self):
        print("Ensuring valid access token...")
        access_token = self.credentials.get("AEP_ACCESS_TOKEN")
        expiry_time = self.credentials.get("AEP_TOKEN_EXPIRY", 0)

        if not access_token or time.time() > expiry_time:
            print("Access token missing or expired. Fetching a new token...")
            return self.refresh_access_token()
        return access_token

    def post_query(self, sql_query, query_name="My Query", description="Description of my query"):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.credentials["AEP_API_KEY"],
            "x-gw-ims-org-id": self.credentials["AEP_ORG_ID"],
            "x-sandbox-name": self.credentials["AEP_SANDBOX_NAME"],
            "Content-Type": "application/json"
        }
        payload = {
            "dbName": "prod:all",  # Use 'prod:all' or a specific database
            "sql": sql_query,
            "name": query_name,
            "description": description
        }

        print("\nPosting query to Adobe Experience Platform Query Service...")
        response = requests.post(self.query_endpoint, headers=headers, json=payload)

        if response.status_code in (201, 202):
            query_id = response.json().get("id")
            print(f"Query created successfully! Query ID: {query_id}")
            return query_id
        else:
            print(f"Failed to create query: {response.status_code}, {response.text}")
            exit()

    def monitor_query(self, query_id):
        """
        Monitor the status of the query until it completes or fails.
        Uses a progress bar for dynamic updates on the same line.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.credentials["AEP_API_KEY"],
            "x-gw-ims-org-id": self.credentials["AEP_ORG_ID"],
            "x-sandbox-name": self.credentials["AEP_SANDBOX_NAME"],
            "Content-Type": "application/json"
        }
        query_info_endpoint = f"{self.query_endpoint}/{query_id}"

        print("\nMonitoring query status...")
        start_time = time.time()
        prev_status = None

        with tqdm(
            desc="Query Progress",
            total=100,
            bar_format="{l_bar}{bar} [Elapsed: {elapsed}] Status: {postfix}",
            dynamic_ncols=True
        ) as progress_bar:
            while True:
                response = requests.get(query_info_endpoint, headers=headers)
                if response.status_code != 200:
                    progress_bar.set_postfix_str("Error fetching status")
                    progress_bar.close()
                    print(f"\nFailed to retrieve query information: {response.status_code}, {response.text}")
                    exit()

                query_info = response.json()
                status = query_info.get("state", "UNKNOWN")
                elapsed_time = time.time() - start_time

                # Only update the progress bar if the status has changed
                if status != prev_status:
                    prev_status = status
                    progress_bar.set_postfix_str(f"{status} | Elapsed Time: {elapsed_time:.2f}s")

                if status == "SUCCESS":
                    progress_bar.n = 100
                    progress_bar.last_print_n = 100
                    progress_bar.update(0)
                    progress_bar.set_postfix_str("Completed")
                    progress_bar.close()
                    print("\nQuery completed successfully!")
                    return query_info
                elif status == "FAILED":
                    progress_bar.n = 100
                    progress_bar.last_print_n = 100
                    progress_bar.update(0)
                    progress_bar.set_postfix_str("Failed")
                    progress_bar.close()
                    print("\nQuery failed!")
                    errors = query_info.get("errors", [])
                    if errors:
                        print("Error details:")
                        for error in errors:
                            print(json.dumps(error, indent=4))
                    exit()
                else:
                    progress_bar.update(5)
                    time.sleep(5)

    def fetch_results(self, query_id, file_name="query_results.csv"):
        """
        Fetch the query results and save to a CSV file.
        """
        results_endpoint = f"{self.query_endpoint}/{query_id}/result"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.credentials["AEP_API_KEY"],
            "x-gw-ims-org-id": self.credentials["AEP_ORG_ID"],
            "x-sandbox-name": self.credentials["AEP_SANDBOX_NAME"],
            "Content-Type": "application/json"
        }

        print("\nFetching query results...")
        response = requests.get(results_endpoint, headers=headers)

        if response.status_code == 200:
            records = response.json()
            print(f"Fetched {len(records)} records.")
            self.save_to_csv(records, file_name)
        else:
            print(f"Failed to fetch query results: {response.status_code}, {response.text}")
            exit()

    def save_to_csv(self, records, file_name):
        if not records:
            print("No records to save.")
            return

        print(f"Saving results to {file_name}...")
        with open(file_name, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        print(f"Results saved to {file_name}.")

# Main execution
if __name__ == "__main__":
    # Initialize the service
    adobe_service = AdobeQueryService()

    # Define SQL query
    sql_query = """
    SELECT
        _citgroup.segmentScoreAttributes.CIT_Cust_seg,
        _citgroup.segmentScoreAttributes.CIF AS CustId,
        _citgroup.segmentScoreAttributes.Open_date,
        _citgroup.segmentScoreAttributes.Period_date
    FROM
        epsilon_segment_score_dataset_v1_2
    LIMIT 10
    """

    # Post query
    query_id = adobe_service.post_query(sql_query, query_name="Test_Customer Segment Query", description="Fetch customer segment data.")

    # Monitor query status
    query_info = adobe_service.monitor_query(query_id)

    # Fetch results and save to CSV
    adobe_service.fetch_results(query_id, file_name="Test_Customer_Segment_Query.csv")
