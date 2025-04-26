import requests
import json
import logging
import time
import os

# Configure logging
logging.basicConfig(
    filename="token_refresh.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AEPTokenRefresher:
    def __init__(self, credentials_file):
        """
        Initialize with the credentials file.
        """
        self.credentials_file = credentials_file
        self.credentials = self.load_credentials()
        self.ims_url = self.credentials["ims_url"]
        self.client_id = self.credentials["client_id"]
        self.client_secret = self.credentials["client_secret"]
        self.scopes = " ".join(self.credentials.get("scopes", []))

    def load_credentials(self):
        """
        Load API credentials from a JSON file.
        """
        try:
            with open(self.credentials_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading credentials: {e}")
            raise

    def update_credentials_file(self, new_token, expires_in):
        """
        Update the credentials file with the new access token and expiration timestamp.
        """
        try:
            expiration_time = int(time.time()) + expires_in  # Calculate expiration
            self.credentials["access_token"] = new_token
            self.credentials["token_expires_at"] = expiration_time

            with open(self.credentials_file, "w") as file:
                json.dump(self.credentials, file, indent=4)
            
            logging.info(f"Access token updated successfully, expires at {expiration_time}.")
            print(f"✔ Access token updated. Expires at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiration_time))}")

        except Exception as e:
            logging.error(f"Error updating credentials file: {e}")
            print(f"❌ Failed to update credentials file: {e}")

    def refresh_token(self):
        """
        Refresh the AEP access token using IMS API.
        """
        token_url = f"{self.ims_url}/ims/token/v2"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scopes
        }

        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            response_json = response.json()

            new_token = response_json["access_token"]
            expires_in = response_json.get("expires_in", 86400)  # Default: 24 hours

            # Update credentials file
            self.update_credentials_file(new_token, expires_in)

            logging.info("Access token refreshed successfully.")
            print("✔ New Access Token:", new_token)
            return new_token
        except requests.RequestException as e:
            logging.error(f"Error refreshing access token: {e}")
            print(f"❌ Failed to refresh access token: {e}")
            raise

    def is_token_expired(self):
        """
        Check if the current token is expired.
        """
        expires_at = self.credentials.get("token_expires_at", 0)
        return time.time() >= expires_at

    def get_access_token(self):
        """
        Retrieve a valid access token, refreshing it if needed.
        """
        if self.is_token_expired():
            print("🔄 Token expired. Refreshing...")
            return self.refresh_token()
        print("✔ Using existing valid token.")
        return self.credentials["access_token"]

if __name__ == "__main__":
    # Dynamically find the credentials file inside the CREDS folder
    credentials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cit-credentials.json"))

    refresher = AEPTokenRefresher(credentials_path)
    refresher.get_access_token()
