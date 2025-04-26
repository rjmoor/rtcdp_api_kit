import os
import json
import time
import logging
import subprocess
import requests

# Logging setup
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "token.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AuthHelper:
    def __init__(self, credentials_path="config/cit-credentials.json"):
        self.credentials_path = credentials_path
        self.credentials = self.load_credentials()

    def load_credentials(self):
        try:
            with open(self.credentials_path, "r") as file:
                self.credentials = json.load(file)
                return self.credentials
        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
            return None

    def is_token_expired(self):
        if not self.credentials:
            self.load_credentials()
        return time.time() >= self.credentials.get("token_expires_at", 0)

    def refresh_token(self):
        try:
            print("[cyan]🔄 Refreshing token via ims.token_refresh.py...[/cyan]")
            subprocess.run(["python3", "config/ims.token_refresh.py"], check=True, capture_output=True, text=True)
            logging.info("Access token refreshed successfully.")
            self.load_credentials()  # Reload updated token
        except subprocess.CalledProcessError as e:
            logging.error(f"Token refresh failed: {e.stderr}")
            print("[red]❌ Token refresh failed. See token.log for details.[/red]")

    def validate_token_with_ping(self):
        self.load_credentials()
        if not self.credentials:
            return False

        test_url = f"{self.credentials['base_url']}/data/core/ups/config/mergePolicies"
        headers = {
            "Authorization": f"Bearer {self.credentials['access_token']}",
            "x-api-key": self.credentials["api_key"],
            "x-gw-ims-org-id": self.credentials["org_id"],
            "x-sandbox-name": self.credentials.get("sandbox", "dev")
        }

        try:
            response = requests.get(test_url, headers=headers)
            if response.status_code == 200:
                logging.info("Token validated successfully with API.")
                return True
            elif response.status_code == 401:
                logging.warning("Token invalid. Refreshing automatically.")
                self.refresh_token()
                return False
            else:
                logging.warning(f"Unexpected token check status: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Token validation request failed: {e}")
            return False

    def get_access_token(self):
        if self.is_token_expired():
            print("[yellow]⚠️ Token expired. Attempting refresh...[/yellow]")
            self.refresh_token()

        if not self.validate_token_with_ping():
            print("[red bold]❌ Token validation failed after refresh.[/red bold]")
            return None

        return self.credentials.get("access_token") if self.credentials else None

    def get_sandbox(self):
        self.load_credentials()
        return self.credentials.get("sandbox", "prod") if self.credentials else None

    def get_org_id(self):
        self.load_credentials()
        return self.credentials.get("org_id") if self.credentials else None

    def get_api_key(self):
        self.load_credentials()
        return self.credentials.get("api_key") if self.credentials else None

    def get_base_url(self):
        self.load_credentials()
        return self.credentials.get("base_url") if self.credentials else None
