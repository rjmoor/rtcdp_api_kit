# cli/inspect_data/queries.py

import os
import yaml
import logging
import time
import requests
from rich import print
from utils.auth_helper import AuthHelper
import csv
import pandas as pd

# Logging setup
LOG_DIR = "logs"
QUERY_LOG = "queries.log"
LAST_QUERY_PATH = os.path.join(LOG_DIR, "last_query.sql")
RESULT_CSV_PATH = os.path.join(LOG_DIR, "last_query_results.csv")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, QUERY_LOG),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

QUERIES_YML_PATH = "queries/queries.yml"

class QueryHandler:
    def __init__(self):
        self.auth = AuthHelper()
        self.base_url = self.auth.get_base_url()
        self.api_key = self.auth.get_api_key()
        self.org_id = self.auth.get_org_id()
        self.sandbox = self.auth.get_sandbox()
        self.token = self.auth.get_access_token()

    def load_queries(self):
        if not os.path.exists(QUERIES_YML_PATH):
            print(f"[yellow]⚠️ No query file found at {QUERIES_YML_PATH}[/yellow]")
            return {}

        try:
            with open(QUERIES_YML_PATH, 'r') as stream:
                return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.error(f"Failed to load YAML: {e}")
            print(f"[red]❌ Error loading queries YAML: {e}[/red]")
            return {}

    def list_queries(self, queries):
        print("\n[bold]📑 AVAILABLE QUERIES[/bold]")
        for key, meta in queries.items():
            print(f"[bold cyan]{key}[/bold cyan]: {meta.get('alias', 'No alias')} - {meta.get('description', 'No description')}")

    def prompt_and_run_query(self):
        queries = self.load_queries()
        if not queries:
            return None

        self.list_queries(queries)
        selected = input("\nEnter query alias or number: ").strip()

        matched_key = None
        for key, meta in queries.items():
            if key == selected or meta.get("alias") == selected:
                matched_key = key
                break

        if not matched_key:
            print("[red]❌ Query not found.[/red]")
            return None

        query_template = queries[matched_key].get("sql", "")
        placeholders = [part.strip("{}") for part in query_template.split() if part.startswith("{{") and part.endswith("}}")]

        filled_query = query_template
        for ph in placeholders:
            user_value = input(f"Enter value for [{ph}]: ")
            filled_query = filled_query.replace(f"{{{{{ph}}}}}", user_value)

        print("\n[bold green]🧠 Final Query to Run:[/bold green]")
        print(filled_query)
        return filled_query

    def submit_query(self, sql):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox,
            "Content-Type": "application/json"
        }
        body = {
            "name": "CLI Query Submission",
            "sql": sql,
            "description": "Submitted via CLI"
        }

        res = requests.post(f"{self.base_url}/data/foundation/query/queries", json=body, headers=headers)
        if res.status_code != 201:
            print(f"[red]❌ Failed to submit query: {res.text}[/red]")
            return None

        query_id = res.json()["id"]
        print(f"[green]🚀 Query submitted. ID: {query_id}[/green]")
        return query_id

    def poll_query_status(self, query_id):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox
        }

        status_url = f"{self.base_url}/data/foundation/query/queries/{query_id}"
        print("⏳ Polling for query completion...")
        while True:
            res = requests.get(status_url, headers=headers)
            state = res.json().get("state", "UNKNOWN")
            print(f"🔄 Status: {state}")
            if state in ["SUCCEEDED", "FAILED", "CANCELED"]:
                break
            time.sleep(5)
        return state

    def handle_queries(self):
        while True:
            print("\n[bold]📑 QUERY OPERATIONS[/bold]")
            print("1️⃣ Run a Saved Query")
            print("2️⃣ Back to Inspect Datalake Menu")

            choice = input("Select an option: ").strip()

            if choice == "1":
                sql = self.prompt_and_run_query()
                if sql:
                    query_id = self.submit_query(sql)
                    if query_id:
                        status = self.poll_query_status(query_id)
                        print(f"[blue]📌 Final Status: {status}[/blue]")

            elif choice == "2":
                break
            else:
                print("[red]❌ Invalid choice. Try again.[/red]")
                
    def save_last_query(self, sql):
        with open(LAST_QUERY_PATH, "w") as f:
            f.write(sql)

    def re_run_last_query(self):
        if not os.path.exists(LAST_QUERY_PATH):
            print("[yellow]⚠️ No previous query found.[/yellow]")
            return

        with open(LAST_QUERY_PATH, "r") as f:
            sql = f.read()

        print(f"[bold green]🧠 Re-running Last Query:[/bold green]\n{sql}")
        query_id = self.submit_query(sql)
        if query_id:
            status = self.poll_query_status(query_id)
            print(f"[blue]📌 Final Status: {status}[/blue]")
            if status == "SUCCEEDED":
                self.download_query_results(query_id)

    def download_query_results(self, query_id):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": self.sandbox
        }

        url = f"{self.base_url}/data/foundation/query/queries/{query_id}/results"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"[red]❌ Could not download results: {res.text}[/red]")
            return

        try:
            rows = res.json().get("rows", [])
            if not rows:
                print("[yellow]⚠️ No results returned.[/yellow]")
                return

            keys = rows[0].keys()
            with open(RESULT_CSV_PATH, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(rows)

            print(f"[green]📁 Results saved to {RESULT_CSV_PATH}[/green]")
        except Exception as e:
            print(f"[red]❌ Failed to process results: {e}[/red]")

    def show_last_results(self):
        if not os.path.exists(RESULT_CSV_PATH):
            print("[yellow]⚠️ No saved results to show.[/yellow]")
            return

        try:
            df = pd.read_csv(RESULT_CSV_PATH)
            print("[bold blue]📊 Last Query Results Preview:[/bold blue]")
            print(df.head(10).to_string(index=False))
        except Exception as e:
            print(f"[red]❌ Failed to read results: {e}[/red]")

    def handle_queries(self):
        while True:
            print("\n[bold]📑 QUERY OPERATIONS[/bold]")
            print("1️⃣ Run a Saved Query")
            print("2️⃣ Re-run Last Query")
            print("3️⃣ Show Last Query Results")
            print("4️⃣ Back to Inspect Datalake Menu")

            choice = input("Select an option: ").strip()

            if choice == "1":
                sql = self.prompt_and_run_query()
                if sql:
                    self.save_last_query(sql)
                    query_id = self.submit_query(sql)
                    if query_id:
                        status = self.poll_query_status(query_id)
                        print(f"[blue]📌 Final Status: {status}[/blue]")
                        if status == "SUCCEEDED":
                            self.download_query_results(query_id)

            elif choice == "2":
                self.re_run_last_query()

            elif choice == "3":
                self.show_last_results()

            elif choice == "4":
                break
            else:
                print("[red]❌ Invalid choice. Try again.[/red]")
