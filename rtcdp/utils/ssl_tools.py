import ssl
import os
import json
import requests
import logging
import certifi  # ✅ Added missing import

# Configure logging
logging.basicConfig(
    filename="adobe_query.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print(ssl.OPENSSL_VERSION)

class AdobeSSLServiceTest:
    def __init__(self, credentials_file, environment_name):
        """
        Initialize the AdobeQueryService instance.

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
            logging.error("❌ Credentials file not found: %s", e)
            raise
        except json.JSONDecodeError as e:
            logging.error("❌ Error decoding JSON from credentials file: %s", e)
            raise

    def get_environment(self, environment_name):
        """Retrieve the sandbox information for the specified environment."""
        for env in self.credentials.get("environments", []):
            if env["name"] == environment_name:
                return env
        raise ValueError(f"❌ Environment '{environment_name}' not found in credentials.")

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
            response = requests.post(token_url, data=payload, verify=certifi.where())  # ✅ Fixed SSL verification
            if response.status_code == 200:
                new_token = response.json()["access_token"]
                self.credentials["access_token"] = new_token
                with open(self.credentials_file, "w") as file:
                    json.dump(self.credentials, file, indent=4)
                logging.info("✔ Access token refreshed successfully.")
                return new_token
            else:
                logging.error("❌ Failed to refresh access token: %s", response.text)
                response.raise_for_status()
        except Exception as e:
            logging.error("❌ Error refreshing access token: %s", e)
            raise

    def get_access_token(self):
        """Ensure a valid access token is available."""
        access_token = self.credentials.get("access_token")
        if not access_token:
            logging.info("⚠️ Access token missing, refreshing...")
            access_token = self.refresh_access_token()
        return access_token

    def run_ssl_test(self):
        url = "https://platform.adobe.io/data/core/ups/config/mergePolicies"
        headers = {
            "Authorization": f"Bearer {self.get_access_token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.environment
        }

        try:
            response = requests.get(url, headers=headers, verify=False)  # 🔴 TEMPORARY
            print(response.status_code, response.text)
        except requests.exceptions.SSLError as e:
            print("SSL Error:", e)

# ✅ **Usage Example**
if __name__ == "__main__":
    creds_path = os.path.join("CREDS", "rol_credentials.json")  # Update path if needed
    environment_name = "Development"

    api = AdobeSSLServiceTest(creds_path, environment_name)
    api_test_results = api.run_ssl_test()
    
    if api_test_results:
        print(json.dumps(api_test_results, indent=4))  # Pretty print response

