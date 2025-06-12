# cli/credentials_cli.py

from rich import print
from rtcdp.api.modules.credentials_data.credentials import CredentialsManager

def credentials_menu():
    manager = CredentialsManager()

    while True:
        print("\n📂 [bold]CREDENTIALS MENU[/bold]")
        print("────────────────────────────")
        print("1️⃣ View Current Credentials")
        print("2️⃣ Validate Credentials File")
        print("3️⃣ Check Access Token Validity")
        print("4️⃣ Generate New Access Token")
        print("5️⃣ Load Credentials File from Path")
        print("6️⃣ Show Token Expiration Countdown")
        print("0️⃣ Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            manager.view_credentials()
        elif choice == "2":
            manager.validate_credentials()
        elif choice == "3":
            manager.check_token_validity()
        elif choice == "4":
            manager.generate_new_access_token()
        elif choice == "5":
            manager.update_credentials_file()
        elif choice == "6":
            manager.show_token_expiry()
        elif choice == "0":
            print("[cyan]🔙 Returning to Main Menu...[/cyan]")
            break
        else:
            print("[red]❌ Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    credentials_menu()
