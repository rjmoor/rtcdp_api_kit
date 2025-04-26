# cli/inspect_dataset/search_namespace.py

import logging
import requests
from rich import print
from utils.auth_helper import AuthHelper

# Logging setup
LOG_DIR = "logs"
NS_LOG = "namespace_search.log"
logging.basicConfig(
    filename=f"{LOG_DIR}/{NS_LOG}",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class NamespaceHandler:
    def __init__(self):
        self.auth = AuthHelper()
        self.base_url = self.auth.get_base_url()
        self.api_key = self.auth.get_api_key()
        self.org_id = self.auth.get_org_id()
        self.sandbox = self.auth.get_sandbox()
        self.token = self.auth.get_access_token()

    def search_datasets_by_namespace(self):
        print("\n[bold]🔍 Search Datasets by Namespace[/bold]")
        namespace = input("Enter identity namespace (e.g. ECID, EMAIL, IDPUSERID): ").strip()

        if not namespace:
            print("[yellow]⚠️ No namespace provided.[/yellow]")
            return

        url = f"{self.base_url}/catalog/dataSets"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            datasets = response.json().get("children", [])

            matched = []
            for ds in datasets:
                schema = ds.get("schema", {})
                if namespace.lower() in str(schema).lower():
                    matched.append(ds)

            if not matched:
                print(f"[yellow]⚠️ No datasets found using namespace '{namespace}'.[/yellow]")
                return

            print(f"\n[green]✔ Found {len(matched)} dataset(s) using namespace '{namespace}':[/green]")
            for i, ds in enumerate(matched, 1):
                print(f"{i}. [bold]{ds.get('name')}[/bold] | ID: {ds.get('id')}")
        except requests.RequestException as e:
            logging.error(f"Namespace dataset search failed: {e}")
            print(f"[red]❌ Request error: {e}[/red]")

    def handle_namespace_search(self):
        while True:
            print("\n[bold]🔍 NAMESPACE SEARCH[/bold]")
            print("1️⃣ Search Datasets by Identity Namespace")
            print("2️⃣ Back to Inspect Datalake Menu")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.search_datasets_by_namespace()
            elif choice == "2":
                break
            else:
                print("[red]❌ Invalid choice. Try again.[/red]")