# modules/segment_data/snapshot_export.py

import requests
from rtcdp.utils.auth_helper import AuthHelper
from rich import print
from datetime import datetime

class SnapshotExporter:
    def __init__(self, auth_helper: AuthHelper):
        self.auth = auth_helper
        self.token = self.auth.get_access_token()
        self.base_url = self.auth.get_base_url()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.auth.get_api_key(),
            "x-gw-ims-org-id": self.auth.get_org_id(),
            "x-sandbox-name": self.auth.get_sandbox(),
            "Content-Type": "application/json"
        }

    def trigger_snapshot(self):
        print("[cyan]📦 Triggering profile snapshot export...[/cyan]")
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        payload = {
            "name": f"Snapshot Export {timestamp}",
            "description": "Generated via RTCDP CLI",
            "profileType": "all",
            "schemaName": "_xdm.context.profile"
        }

        try:
            url = f"{self.base_url}/data/core/ups/profileSnapshots"
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code in [200, 201, 202]:
                print("[green]✔ Snapshot export started successfully.[/green]")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"[red]❌ Snapshot failed: {response.text}[/red]")
        except Exception as e:
            print(f"[red]❌ Error triggering snapshot: {e}[/red]")
