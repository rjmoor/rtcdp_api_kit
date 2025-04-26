# modules/segment_data/audience_handler.py

import requests
import logging
from utils.auth_helper import AuthHelper
from rich import print

class AudienceHandler:
    def __init__(self, auth_helper: AuthHelper):
        self.auth = auth_helper
        self.base_url = f"{self.auth.get_base_url()}/audiences"
        self.token = self.auth.get_access_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.auth.get_api_key(),
            "x-gw-ims-org-id": self.auth.get_org_id(),
            "x-sandbox-name": self.auth.get_sandbox(),
            "Content-Type": "application/json"
        }

    def list_audiences(self):
        print("[cyan]📋 Fetching existing audiences...[/cyan]")
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            data = response.json().get("children", [])
            for idx, audience in enumerate(data, 1):
                print(f"{idx}. {audience.get('name')} (ID: {audience.get('id')})")
        except Exception as e:
            print(f"[red]❌ Failed to list audiences: {e}[/red]")

    def create_audience(self, name, description, pql_expr):
        payload = {
            "name": name,
            "description": description,
            "type": "SegmentDefinition",
            "expression": {
                "type": "PQL",
                "format": "pql/text",
                "value": pql_expr
            },
            "schema": {
                "name": "_xdm.context.profile"
            }
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            print("[green]✔ Audience created successfully![/green]")
            print(response.json())
        except Exception as e:
            print(f"[red]❌ Failed to create audience: {e}[/red]")

    def delete_audience(self, audience_id):
        try:
            response = requests.delete(f"{self.base_url}/{audience_id}", headers=self.headers)
            if response.status_code == 204:
                print(f"[green]✔ Audience {audience_id} deleted.[/green]")
            else:
                print(f"[yellow]⚠️ Response: {response.status_code}[/yellow]")
        except Exception as e:
            print(f"[red]❌ Error deleting audience: {e}[/red]")

    def get_audience_by_id(self, audience_id):
        try:
            response = requests.get(f"{self.base_url}/{audience_id}", headers=self.headers)
            response.raise_for_status()
            print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"[red]❌ Failed to retrieve audience: {e}[/red]")
