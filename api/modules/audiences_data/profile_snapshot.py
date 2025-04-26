import json
import requests
import logging
import os
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="/logs/snapshot_export.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ProfileSnapshotExporter:
    def __init__(self, credentials_file, environment):
        self.credentials_file = credentials_file
        self.credentials = self.load_credentials()
        self.base_url = self.credentials["base_url"]
        self.api_key = self.credentials["api_key"]
        self.org_id = self.credentials["org_id"]
        self.environment = environment

    def load_credentials(self):
        try:
            with open(self.credentials_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"❌ Error loading credentials: {e}")
            raise

    def refresh_token(self):
        try:
            print("🔄 Refreshing OAuth Token...")
            subprocess.run(["python3", "../ims.token_refresh.py"], check=True)
            logging.info("✔ Token refreshed successfully.")
            print("✔ Token refreshed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Failed to refresh token: {e}")
            raise RuntimeError("❌ Token refresh failed. Check logs for details.")

    def get_access_token(self):
        access_token = self.credentials.get("access_token")

        if not access_token:
            print("⚠️ No access token found. Attempting to refresh token...")
            self.refresh_token()
            self.credentials = self.load_credentials()
            return self.credentials.get("access_token")

        # Validate token
        test_url = f"{self.base_url}/data/core/ups/config/mergePolicies"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.environment["sandbox_id"]
        }

        response = requests.get(test_url, headers=headers)

        if response.status_code == 401:
            logging.warning("⚠️ OAuth token is invalid. Refreshing token...")
            self.refresh_token()
            self.credentials = self.load_credentials()
            return self.credentials.get("access_token")

        return access_token

    def trigger_profile_snapshot(self):
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/data/core/ups/profileSnapshots"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-api-key": self.api_key,
                "x-gw-ims-org-id": self.org_id,
                "x-sandbox-name": self.environment["sandbox_id"],
                "Content-Type": "application/json"
            }

            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
            payload = {
                "name": f"Snapshot - Merge Audit {timestamp}",
                "description": "Triggered snapshot for post-merge policy validation",
                "profileType": "all",
                "schemaName": "_xdm.context.profile"
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201, 202]:
                logging.info("✔ Snapshot export initiated successfully.")
                print("✔ Snapshot export triggered.")
                print("📦 Snapshot Info:", json.dumps(response.json(), indent=2))
            else:
                logging.error(f"❌ Snapshot export failed: {response.text}")
                print(f"❌ Snapshot export failed: {response.text}")

        except Exception as e:
            logging.error(f"❌ Error during snapshot export: {e}")
            print(f"❌ Error during snapshot export: {e}")

# === Menu for Snapshot Export ===
def main():
    credentials_path = os.path.join("..", "CREDS", "cit_credentials.json")

    with open(credentials_path, "r") as file:
        credentials = json.load(file)

    environments = credentials.get("environments", [])

    print("\n🌍 Available Environments:")
    for idx, env in enumerate(environments, 1):
        print(f"{idx}. {env['name']}")

    try:
        selection = int(input("\nSelect an environment (number): ")) - 1
        if selection < 0 or selection >= len(environments):
            print("❌ Invalid environment selection.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return

    selected_environment = environments[selection]
    exporter = ProfileSnapshotExporter(credentials_path, selected_environment)
    exporter.trigger_profile_snapshot()

if __name__ == "__main__":
    main()
