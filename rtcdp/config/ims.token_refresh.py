import os
import json
import time
import logging
import requests

# === Setup Logging ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "token.log"),
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
                creds = json.load(file)
                if not isinstance(creds, dict):
                    raise ValueError("Credentials file is not a valid JSON object.")
                return creds
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error loading credentials: {e}")
            print(f"❌ Failed to load credentials: {e}", flush=True)
            return {}

    def update_credentials_file(self, new_token, expires_in):
        """
        Update the credentials file with the new access token and expiration timestamp.
        """
        try:
            expiration_time = int(time.time()) + expires_in
            self.credentials["access_token"] = new_token
            self.credentials["token_expires_at"] = expiration_time

            with open(self.credentials_file, "w") as file:
                json.dump(self.credentials, file, indent=4)

            logging.info(f"✔ Access token updated successfully, expires at {expiration_time}.")
            print(f"✔ Access token updated. Expires at [bold cyan]{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiration_time))}[/bold cyan]", flush=True)

        except Exception as e:
            logging.error(f"Error updating credentials file: {e}")
            print(f"❌ Failed to update credentials file: {e}", flush=True)

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
            expires_in = response_json.get("expires_in", 86400)

            self.update_credentials_file(new_token, expires_in)
            logging.info("✔ Token refreshed successfully.")
            print("✔ New Access Token:", new_token, flush=True)
            return new_token

        except requests.RequestException as e:
            logging.error(f"❌ Token refresh failed: {e}")
            print(f"❌ Failed to refresh access token: {e}", flush=True)
            return None

    def is_token_expired(self):
        """
        Check if the current token is expired.
        """
        expires_at = self.credentials.get("token_expires_at", 0)
        return time.time() >= expires_at

    def get_access_token(self):
        """
        Get valid access token or refresh if expired.
        """
        if not self.credentials:
            print("⚠️ No valid credentials loaded.", flush=True)
            return None

        if self.is_token_expired():
            print("🔄 Token expired. Refreshing...", flush=True)
            return self.refresh_token()

        print("✔ Using existing valid token.", flush=True)
        return self.credentials.get("access_token")


# === Entry point for subprocess execution ===
if __name__ == "__main__":
    credentials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cit-credentials.json"))
    refresher = AEPTokenRefresher(credentials_path)

    token = refresher.get_access_token()
    if token:
        logging.info("✅ Token refresh script completed successfully.")
        print("✅ Token refresh complete.", flush=True)
    else:
        logging.error("❌ Token refresh script failed.")
        print("❌ Token refresh failed.", flush=True)
