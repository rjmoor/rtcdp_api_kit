# modules/dataset_data/dataset.py

import json
import os
import logging
import requests
from rich import print
from rtcdp.utils.auth_helper import AuthHelper

# Configure Logging
LOG_DIR = "logs"
DATASET_LOG = "datasets.log"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f"{LOG_DIR}/{DATASET_LOG}",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DatasetManager:
    def __init__(self):
        self.auth = AuthHelper()
        self.base_url = self.auth.get_base_url()
        self.api_key = self.auth.get_api_key()
        self.org_id = self.auth.get_org_id()
        self.sandbox = self.auth.get_sandbox()
        self.token = self.auth.get_access_token()

    def list_datasets(self):
        print("[cyan]\n📦 Fetching all datasets with pagination...[/cyan]")
        all_datasets = []
        limit = 20
        offset = 0

        while True:
            url = f"{self.base_url}/data/foundation/catalog/dataSets?limit={limit}&start={offset}&sandboxId={self.sandbox}"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "x-api-key": self.api_key,
                "x-gw-ims-org-id": self.org_id,
                "Accept": "application/json"
            }

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                datasets = [
                    {"id": dataset_id, "name": info.get("name", "Unnamed Dataset"), **info}
                    for dataset_id, info in data.items()
                ]

                if not datasets:
                    break

                all_datasets.extend(datasets)
                offset += limit
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching datasets: {e}")
                print(f"[red]❌ Error fetching datasets: {e}[/red]")
                break

        for i, ds in enumerate(all_datasets, 1):
            print(f"{i}. [bold]{ds['name']}[/bold] ({ds['id']})")
        return all_datasets

    def create_datasets(self):
        print("\n[bold cyan]🆕 Create New Dataset[/bold cyan]")
        name = input("Dataset Name: ").strip()
        schema_ref = input("Schema Reference (e.g. https://ns.adobe.com/xdm/context/profile): ").strip()

        payload = {
            "name": name,
            "schemaRef": {
                "id": schema_ref,
                "contentType": "application/vnd.adobe.xed+json;version=1"
            },
            "fileDescription": {
                "format": "json"
            }
        }

        url = f"{self.base_url}/data/foundation/catalog/dataSets"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"[green]✔ Dataset created successfully. ID: {result.get('id')}[/green]")
            logging.info(f"Created dataset: {result}")
        except requests.RequestException as e:
            logging.error(f"Dataset creation failed: {e}")
            print(f"[red]❌ Failed to create dataset: {e}[/red]")

    def ingest_data(self):
        print("\n[bold cyan]📥 Ingest Data[/bold cyan]")
        dataset_id = input("Enter Dataset ID: ").strip()
        record = input("Enter JSON record (as string): ").strip()

        try:
            json_record = json.loads(record)
        except json.JSONDecodeError:
            print("[red]❌ Invalid JSON format.[/red]")
            return

        payload = [json_record]
        url = f"{self.base_url}/data/foundation/import/dataSets/{dataset_id}/batches"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print("[green]✔ Data ingested successfully.[/green]")
            logging.info("Data ingested successfully.")
        except requests.RequestException as e:
            logging.error(f"Data ingestion failed: {e}")
            print(f"[red]❌ Failed to ingest data: {e}[/red]")

    def delete_datasets(self):
        datasets = self.list_datasets()
        if not datasets:
            print("[yellow]⚠ No datasets to delete.[/yellow]")
            return

        print("\nSelect dataset to delete:")
        for i, ds in enumerate(datasets, 1):
            print(f"{i}. {ds['name']} ({ds['id']})")
        print(f"{len(datasets) + 1}. Cancel")

        try:
            choice = int(input("Select number: "))
            if 1 <= choice <= len(datasets):
                dataset_id = datasets[choice - 1]["id"]
                url = f"{self.base_url}/data/foundation/catalog/dataSets/{dataset_id}"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "x-api-key": self.api_key,
                    "x-gw-ims-org-id": self.org_id,
                    "x-sandbox-name": self.sandbox
                }

                response = requests.delete(url, headers=headers)
                response.raise_for_status()
                print("[green]✔ Dataset deleted successfully.[/green]")
                logging.info(f"Deleted dataset ID: {dataset_id}")
            else:
                print("Canceling.")
        except Exception as e:
            logging.error(f"Failed to delete dataset: {e}")
            print(f"[red]❌ Failed to delete: {e}[/red]")

    def metadata_keys_menu(self, entity):
        keys = list(entity.keys())
        while True:
            print("\n[bold]Metadata Keys for Selected Dataset:[/bold]")
            for idx, key in enumerate(keys, 1):
                print(f"{idx}. {key}")
            print(f"{len(keys)+1}. Exit")

            try:
                choice = int(input("Select a metadata key to view its value: "))
                if 1 <= choice <= len(keys):
                    key = keys[choice - 1]
                    value = entity.get(key, "No value available")
                    print(f"\n{key}: {json.dumps(value, indent=2)}")
                elif choice == len(keys) + 1:
                    print("Exiting metadata keys menu.")
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def browse_datasets_menu(self):
        datasets = self.list_datasets()
        if not datasets:
            print("[yellow]⚠️ No datasets found.[/yellow]")
            return

        while True:
            print("\nSelect a dataset to view metadata keys:")
            for idx, ds in enumerate(datasets, 1):
                print(f"{idx}. {ds['name']} ({ds['id']})")
            print(f"{len(datasets)+1}. Exit")

            try:
                choice = int(input("Enter your choice: "))
                if 1 <= choice <= len(datasets):
                    self.metadata_keys_menu(datasets[choice - 1])
                elif choice == len(datasets) + 1:
                    print("Exiting dataset menu.")
                    break
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

