# modules/credentials_data/credentials

import json
import os
import logging
import time
from datetime import datetime, timedelta
import requests
from rich import print
from rtcdp.utils.auth_helper import AuthHelper

# Configure Logging
LOG_DIR = "logs"
DATASET_LOG = "credentials.log"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f"{LOG_DIR}/{DATASET_LOG}",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class CredentialsManager:
    def __init__(self):
        self.auth = AuthHelper()

    def view_credentials(self):
        creds = self.auth.load_credentials()
        if creds:
            print("\n[bold cyan]🔐 Current Credentials:[/bold cyan]")
            print(json.dumps(creds, indent=2))

    def validate_credentials(self):
        creds = self.auth.load_credentials()
        required_fields = ["base_url", "api_key", "org_id", "access_token"]
        if not creds:
            return

        print("\n[cyan]🔎 Validating credentials file...[/cyan]")
        missing = [field for field in required_fields if field not in creds]
        if missing:
            print(f"[red]❌ Missing fields: {', '.join(missing)}[/red]")
        else:
            print("[green]✅ Credentials file is valid.[/green]")

    def check_token_validity(self):
        token = self.auth.get_access_token()
        if token:
            print("[green]✔ Token is valid and authorized.[/green]")
        else:
            print("[red]❌ Token could not be validated.[/red]")

    def generate_new_access_token(self):
        self.auth.refresh_token()
        token = self.auth.get_access_token()
        if token:
            print("[green]✔ New Access Token Loaded.[/green]")
        else:
            print("[red]❌ Token refresh failed.[/red]")

    def update_credentials_file(self):
        file_path = input("\n📥 Enter full path to your new credential file (JSON): ").strip()
        if not os.path.exists(file_path):
            print("[red]❌ File not found.[/red]")
            return

        try:
            with open(file_path, "r") as file:
                new_creds = json.load(file)

            required_fields = ["base_url", "api_key", "org_id", "client_id", "client_secret", "refresh_token"]
            missing = [key for key in required_fields if key not in new_creds]
            if missing:
                print(f"[red]❌ Missing required fields: {', '.join(missing)}[/red]")
                return

            new_creds["sandbox"] = new_creds.get("sandbox", "prod")

            with open(self.auth.credentials_path, "w") as out_file:
                json.dump(new_creds, out_file, indent=2)

            print("[green]✅ New credentials loaded into active config.[/green]")
            logging.info("Credentials updated from file input.")
        except Exception as e:
            print(f"[red]❌ Failed to load credential file: {e}[/red]")
            logging.error(f"Failed to update credentials file: {e}")

    def show_token_expiry(self):
        creds = self.auth.load_credentials()
        if not creds or "token_expires_at" not in creds:
            print("[yellow]⚠️ Token expiration time not found in credentials.[/yellow]")
            return

        expires_at = creds["token_expires_at"]
        now = time.time()
        remaining = int(expires_at - now)

        if remaining <= 0:
            print("[red bold]❌ Token has expired.[/red bold]")
            return

        remaining_td = timedelta(seconds=remaining)
        exp_time = datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')

        if remaining <= 900:
            print(f"[yellow bold]⚠️ Token is expiring soon![/yellow bold] [bold]{remaining_td}[/bold] left until [bold]{exp_time}[/bold]")
        else:
            print(f"[green]✔ Token is valid[/green] until [bold]{exp_time}[/bold] ([cyan]{remaining_td} remaining[/cyan])")