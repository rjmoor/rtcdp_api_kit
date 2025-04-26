#  cli/inspect_data/queries.py

import os
import yaml
import logging
from rich import print
from utils.auth_helper import AuthHelper

# Logging setup
LOG_DIR = "logs"
QUERY_LOG = "queries.log"
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
                queries = yaml.safe_load(stream)
                return queries
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
            return

        self.list_queries(queries)
        selected = input("\nEnter query alias or number: ").strip()

        matched_key = None
        for key, meta in queries.items():
            if key == selected or meta.get("alias") == selected:
                matched_key = key
                break

        if not matched_key:
            print("[red]❌ Query not found.[/red]")
            return

        query_template = queries[matched_key].get("sql", "")
        placeholders = [part.strip("{}") for part in query_template.split() if part.startswith("{{") and part.endswith("}}")]

        filled_query = query_template
        for ph in placeholders:
            user_value = input(f"Enter value for [{ph}]: ")
            filled_query = filled_query.replace(f"{{{{{ph}}}}}", user_value)

        print("\n[bold green]🧠 Final Query to Run:[/bold green]")
        print(filled_query)

        # TODO: Add support to submit this query to the Query Service API
        print("[yellow]⚠️ Query execution not yet implemented.[/yellow]")

    def handle_queries(self):
        while True:
            print("\n[bold]📑 QUERY OPERATIONS[/bold]")
            print("1️⃣ Run a Saved Query")
            print("2️⃣ Back to Inspect Datalake Menu")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.prompt_and_run_query()
            elif choice == "2":
                break
            else:
                print("[red]❌ Invalid choice. Try again.[/red]")
