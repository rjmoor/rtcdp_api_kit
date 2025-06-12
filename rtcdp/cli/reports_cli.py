# rtcdp/cli/reports_cli.py

from rtcdp.cli.query_cli import query_menu
from rtcdp.cli.report_cli import report_menu

def reports_menu():
    while True:
        print("\n📊 [bold]QUERIES & REPORTS MENU[/bold]")
        print("─────────────────────────────────────────")
        print("1️⃣ Run or Inspect Saved Queries")
        print("2️⃣ View or Export Query Results")
        print("0️⃣ Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            query_menu()
        elif choice == "2":
            report_menu()
        elif choice == "0":
            break
        else:
            print("[red]❌ Invalid choice. Try again.[/red]")
