from rich import print
from rtcdp.api.modules.schema_data.schemas import SchemaManager

def schema_menu():
    manager = SchemaManager()

    while True:
        print("\n[bold]📘 SCHEMA OPERATIONS[/bold]")
        print("────────────────────────────────────")
        print("1️⃣ List Schemas")
        print("2️⃣ Get Schema by ID")
        print("3️⃣ Create Schema")
        print("4️⃣ Update Schema (PUT)")
        print("5️⃣ Patch Schema (JSON Patch)")
        print("6️⃣ Delete Schema")
        print("0️⃣ Back to Inspect Datalake Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            manager.list_schemas()
        elif choice == "2":
            container = input("Enter container (tenant/global): ").strip() or "tenant"
            schema_id = input("Enter schema ID or meta:altId: ").strip()
            manager.get_schema_by_id(container, schema_id)
        elif choice == "3":
            manager.create_schema()
        elif choice == "4":
            manager.update_schema()
        elif choice == "5":
            manager.patch_schema()
        elif choice == "6":
            manager.delete_schema()
        elif choice == "0":
            print("[cyan]🔙 Returning to Inspect Datalake Menu...[/cyan]")
            break
        else:
            print("[red]❌ Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    schema_menu()
