# cli/inspect_data/lookup_identity.py

import logging
import requests
from rich import print
from utils.auth_helper import AuthHelper

# Logging setup
LOG_DIR = "logs"
IDENTITY_LOG = "identity_lookup.log"
logging.basicConfig(
    filename=f"{LOG_DIR}/{IDENTITY_LOG}",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class IdentityHandler:
    def __init__(self):
        self.auth = AuthHelper()
        self.base_url = self.auth.get_base_url()
        self.api_key = self.auth.get_api_key()
        self.org_id = self.auth.get_org_id()
        self.sandbox = self.auth.get_sandbox()
        self.token = self.auth.get_access_token()

    def lookup_profile(self):
        print("\n[bold]🧬 Lookup Profile by Identity[/bold]")
        namespace = input("Enter identity namespace (e.g. ECID, IDPUSERID, EMAIL): ").strip()
        identity_value = input("Enter identity value: ").strip()

        if not namespace or not identity_value:
            print("[yellow]⚠️ Both namespace and value are required.[/yellow]")
            return

        url = f"{self.base_url}/profile/entities?entityIdNS={namespace}&entityId={identity_value}"
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
            profile = response.json()

            if not profile:
                print("[yellow]⚠️ No profile found for the given identity.[/yellow]")
                return

            print("\n[green]✔ Profile Found:[/green]")
            print(profile)

        except requests.RequestException as e:
            logging.error(f"Profile lookup failed: {e}")
            print(f"[red]❌ Request error: {e}[/red]")

    def handle_identity_lookup(self):
        while True:
            print("\n[bold]🧬 PROFILE LOOKUP[/bold]")
            print("1️⃣ Lookup Profile by Namespace + ID")
            print("2️⃣ Back to Inspect Datalake Menu")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.lookup_profile()
            elif choice == "2":
                break
            else:
                print("[red]❌ Invalid choice. Try again.[/red]")
