# rtcdp/cli/report_cli.py

import os
import pandas as pd
from rich import print

RESULT_CSV_PATH = "logs/last_query_results.csv"

def report_menu():
    while True:
        print("\n🗂️ [bold]REPORT MENU[/bold]")
        print("1️⃣ Show Last Results as Table")
        print("2️⃣ Export Last Results to JSON")
        print("0️⃣ Back to Queries & Reports")

        choice = input("Select an option: ").strip()

        if not os.path.exists(RESULT_CSV_PATH):
            print("[yellow]⚠️ No results available. Run a query first.[/yellow]")
            return

        if choice == "1":
            df = pd.read_csv(RESULT_CSV_PATH)
            print("[bold green]📊 Showing first 10 rows:[/bold green]")
            print(df.head(10).to_string(index=False))

        elif choice == "2":
            df = pd.read_csv(RESULT_CSV_PATH)
            json_path = RESULT_CSV_PATH.replace(".csv", ".json")
            df.to_json(json_path, orient="records", indent=2)
            print(f"[green]✅ Exported to {json_path}[/green]")

        elif choice == "0":
            break
        else:
            print("[red]❌ Invalid input. Try again.[/red]")
