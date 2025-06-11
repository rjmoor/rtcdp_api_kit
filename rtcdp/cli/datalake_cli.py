# cli/datalake_cli.py

from rich import print

def datalake_menu():
    while True:
        print("\n📂 [bold]INSPECT DATALAKE MENU[/bold]")
        print("────────────────────────────────────")
        print("1️⃣ List Available Schemas")
        print("2️⃣ View Datasets")
        print("3️⃣ Run a Common Query")
        print("4️⃣ Search Datasets by Namespace")
        print("5️⃣ Lookup Profile by Identity")
        print("6️⃣ View Segmentation Services")
        print("0️⃣ Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            from cli.schema_cli import schema_menu
            schema_menu()
        elif choice == "2":
            from cli.dataset_cli import dataset_menu
            dataset_menu()
        elif choice == "3":
            from modules.inspect_data.queries import QueryHandler
            query_handler = QueryHandler()
            query_handler.handle_queries()
        elif choice == "4":
            from modules.inspect_data.search_namespace import NamespaceHandler
            namespace_handler = NamespaceHandler()
            namespace_handler.handle_namespace_search()
        elif choice == "5":
            from modules.inspect_data.lookup_identity import IdentityHandler
            identity_handler = IdentityHandler()
            identity_handler.handle_identity_lookup()
        elif choice == "6":
            from cli.segments_cli import SegmentHandler
            from utils.auth_helper import AuthHelper
            auth = AuthHelper()
            segment_handler = SegmentHandler(auth)
            segment_handler.run_cli()
        elif choice == "0":
            print("🔙 Returning to Main Menu...")
            break
        else:
            print("[red]❌ Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    datalake_menu()

