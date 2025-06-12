from rich import print
from rtcdp.api.modules.dataset_data.datasets import DatasetManager

def dataset_menu():
    manager = DatasetManager()
    
    while True:
        print("\n[bold]📦 DATASET OPERATIONS[/bold]")
        print("────────────────────────────────────")
        print("1️⃣ List Datasets")
        print("2️⃣ Create a Dataset")
        print("3️⃣ Ingest Data into a Dataset")
        print("4️⃣ Delete a Dataset")
        print("5️⃣ Browse Metadata")
        print("0️⃣ Back to Inspect Datalake Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            manager.list_datasets()
        elif choice == "2":
            manager.create_datasets()
        elif choice == "3":
            manager.ingest_data()
        elif choice == "4":
            manager.delete_datasets()
        elif choice == "5":
            manager.browse_datasets_menu()
        elif choice == "0":
            break
        else:
            print("[red]❌ Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    dataset_menu()