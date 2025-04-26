import json
import os
import logging
import requests
from rich import print
from utils.auth_helper import AuthHelper

# Configure Logging
LOG_DIR = "logs"
SCHEMA_LOG = "schemas.log"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f"{LOG_DIR}/{SCHEMA_LOG}",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SchemaManager:
    def __init__(self):
        self.auth = AuthHelper()
        self.base_url = f"{self.auth.get_base_url()}/data/foundation/schemaregistry"
        self.api_key = self.auth.get_api_key()
        self.org_id = self.auth.get_org_id()
        self.sandbox = self.auth.get_sandbox()
        self.token = self.auth.get_access_token()

    def list_schemas(self, container="tenant"):
        print("[cyan]\n📘 Listing Schemas...[/cyan]")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Accept": "application/vnd.adobe.xed-id+json"
        }
        url = f"{self.base_url}/{container}/schemas"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            schemas = response.json().get("results", [])

            if not schemas:
                print("[yellow]⚠ No schemas found.[/yellow]")
                return []

            for i, schema in enumerate(schemas, 1):
                print(f"{i}. [bold]{schema.get('title', 'No Title')}[/bold] | ID: {schema.get('$id', 'N/A')}")
            return schemas

        except requests.RequestException as e:
            print(f"[red]❌ Failed to list schemas: {e}[/red]")
            logging.error(f"Failed to list schemas: {e}")
            return []

    def get_schema_by_id(self, container, schema_id):
        print(f"[cyan]\n🔍 Retrieving schema {schema_id}...[/cyan]")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Accept": "application/vnd.adobe.xed-full+json; version=1"
        }
        url = f"{self.base_url}/{container}/schemas/{schema_id}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            schema_details = response.json()
            print(json.dumps(schema_details, indent=2))
            return schema_details

        except requests.RequestException as e:
            print(f"[red]❌ Failed to retrieve schema: {e}[/red]")
            logging.error(f"Failed to retrieve schema {schema_id}: {e}")
            return None

    def create_schema(self):
        print("\n[cyan]🆕 Create New Schema[/cyan]")
        title = input("Schema Title: ").strip()
        description = input("Schema Description: ").strip()
        ref = input("Enter the class or field group $ref to extend from (comma-separated if multiple): ").strip()
        allOf = [{"$ref": r.strip()} for r in ref.split(",") if r.strip()]

        payload = {
            "type": "object",
            "title": title,
            "description": description,
            "allOf": allOf
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}/tenant/schemas"

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            new_schema = response.json()
            print(f"[green]✔ Schema created. ID: {new_schema.get('$id')}[/green]")
            logging.info(f"Created schema: {new_schema}")
        except requests.RequestException as e:
            print(f"[red]❌ Failed to create schema: {e}[/red]")
            logging.error(f"Schema creation failed: {e}")

    def delete_schema(self):
        schema_id = input("Enter schema ID to delete: ").strip()
        url = f"{self.base_url}/tenant/schemas/{schema_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox
        }

        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 204:
                print("[green]✔ Schema deleted successfully.[/green]")
                logging.info(f"Deleted schema ID: {schema_id}")
            else:
                print(f"[red]❌ Failed to delete schema: {response.status_code}[/red]")
        except Exception as e:
            print(f"[red]❌ Error deleting schema: {e}[/red]")
            logging.error(f"Error deleting schema {schema_id}: {e}")

    def update_schema(self):
        print("[cyan]\n✏ Update Schema[/cyan]")
        schema_id = input("Enter schema ID to update: ").strip()
        print("You will now re-enter the full schema details.")
        title = input("Schema Title: ").strip()
        description = input("Schema Description: ").strip()
        ref = input("Enter allOf $refs (comma-separated): ").strip()
        allOf = [{"$ref": r.strip()} for r in ref.split(",") if r.strip()]

        payload = {
            "type": "object",
            "title": title,
            "description": description,
            "allOf": allOf
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}/tenant/schemas/{schema_id}"

        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            print("[green]✔ Schema updated successfully.[/green]")
            logging.info(f"Updated schema ID: {schema_id}")
        except Exception as e:
            print(f"[red]❌ Failed to update schema: {e}[/red]")
            logging.error(f"Update error for schema {schema_id}: {e}")

    def patch_schema(self):
        print("[cyan]\n🔧 Patch Schema Attributes[/cyan]")
        schema_id = input("Enter schema ID: ").strip()
        op = input("Operation (add, remove, replace): ").strip()
        path = input("JSON Pointer Path (e.g., /meta:immutableTags/-): ").strip()
        value = input("Value (for add/replace): ").strip()

        payload = [{"op": op, "path": path, "value": value}]
        url = f"{self.base_url}/tenant/schemas/{schema_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Content-Type": "application/json"
        }

        try:
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            print("[green]✔ Schema patched successfully.[/green]")
            logging.info(f"Patched schema ID: {schema_id} with {payload}")
        except Exception as e:
            print(f"[red]❌ Patch failed: {e}[/red]")
            logging.error(f"Patch failed for {schema_id}: {e}")
