import json
import requests
import logging
import os
import subprocess
import time

# Configure logging
logging.basicConfig(
    filename="segment_export.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SegmentExporter:
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

    def trigger_segment_job(self, segment_id):
        access_token = self.get_access_token()
        url = f"{self.base_url}/data/core/ups/segment/jobs"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.environment["sandbox_id"],
            "Content-Type": "application/json"
        }

        payload = [{"segmentId": segment_id}]
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            job_info = response.json()
            segment_job_id = job_info["id"]
            logging.info(f"✔ Segment job created. ID: {segment_job_id}")
            print(f"✔ Segment job created. ID: {segment_job_id}")
            return segment_job_id
        else:
            logging.error(f"❌ Failed to create segment job: {response.text}")
            print(f"❌ Failed to create segment job: {response.text}")
            return None

    def export_segment_to_dataset(self, segment_id, dataset_id, merge_policy_id):
        access_token = self.get_access_token()
        url = f"{self.base_url}/data/core/ups/export/jobs"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.environment["sandbox_id"],
            "Content-Type": "application/json"
        }

        payload = {
            "segmentId": segment_id,
            "datasetId": dataset_id,
            "mergePolicyId": merge_policy_id,
            "name": "Stitched Profiles Snapshot Export"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            export_job = response.json()
            export_job_id = export_job["id"]
            logging.info(f"✔ Export job created. ID: {export_job_id}")
            print(f"✔ Export job created. ID: {export_job_id}")
            return export_job_id
        else:
            logging.error(f"❌ Failed to create export job: {response.text}")
            print(f"❌ Failed to create export job: {response.text}")
            return None

    def monitor_export_status(self, job_id):
        access_token = self.get_access_token()
        url = f"{self.base_url}/data/core/ups/export/jobs/{job_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.environment["sandbox_id"]
        }

        print("⏳ Monitoring export job status...")
        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                status = response.json().get("status")
                print(f"🔍 Export status: {status}")
                if status == "SUCCEEDED":
                    print("🎉 Export completed successfully!")
                    break
                elif status in ["FAILED", "CANCELLED"]:
                    print(f"❌ Export failed with status: {status}")
                    break
                else:
                    time.sleep(10)
            else:
                print(f"❌ Failed to fetch export status: {response.text}")
                break

# === Terminal Entry Point ===
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

    segment_id = input("🔢 Enter Segment Definition ID: ").strip()
    dataset_id = input("📦 Enter Target Dataset ID: ").strip()
    merge_policy_id = input("🧩 Enter Merge Policy ID: ").strip()

    selected_env = environments[selection]
    exporter = SegmentExporter(credentials_path, selected_env)

    job_id = exporter.export_segment_to_dataset(segment_id, dataset_id, merge_policy_id)
    if job_id:
        exporter.monitor_export_status(job_id)

if __name__ == "__main__":
    main()
