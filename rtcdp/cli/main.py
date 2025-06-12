# cli/main_cli.py

import os
from rich import print
import logging

# Configure Logging
LOG_DIR = "logs"
DATASET_LOG = "main_menu.log"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f"{LOG_DIR}/{DATASET_LOG}",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def launch_menu():
    while True:
        print("\n📘 [bold]RTCDP API KIT – MAIN MENU[/bold]")
        print("──────────────────────────────────────")
        print("1️⃣ Credentials")
        print("2️⃣ Datasets & Schemas")
        print("3️⃣ Segmentation")
        print("4️⃣ Queries & Reports")
        print("5️⃣ Configuration")
        print("6️⃣ Troubleshooting")
        print("0️⃣ Exit")

        choice = input("\nSelect a menu option: ").strip()

        if choice == "1":
            from rtcdp.cli.credentials_cli import credentials_menu
            logging.info("Credentials menu selected.")
            credentials_menu()

        elif choice == "2":
            from rtcdp.cli.datalake_cli import datalake_menu
            logging.info("Datasets & Schemas menu selected.")
            datalake_menu()

        elif choice == "3":
            from rtcdp.cli.segments_cli import segments_menu
            logging.info("Segmentation menu selected.")
            segments_menu()

        elif choice == "4":
            from rtcdp.cli.reports_cli import reports_menu
            logging.info("Queries & Reports menu selected.")
            reports_menu()

        elif choice == "5":
            from rtcdp.cli.configure_cli import configure_menu
            logging.info("Configuration menu selected.")
            configure_menu()

        elif choice == "6":
            from rtcdp.cli.troubleshoot_cli import troubleshoot_menu
            logging.info("Troubleshooting menu selected.")
            troubleshoot_menu()

        elif choice == "0":
            print("\n[cyan]👋 Goodbye, Architect. RTCDP Kit Closed.[/cyan]")
            break

        else:
            print("[red]❌ Invalid input. Please choose a valid option.[/red]")

 