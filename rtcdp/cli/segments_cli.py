# rtcdp/cli/segments_cli.py
from rtcdp.utils.auth_helper import AuthHelper
from api.modules.segment_data.audience import AudienceHandler
from api.modules.segment_data.segment import SegmentManager
from api.modules.segment_data.snapshot import SnapshotExporter
from rich import print

def segments_menu():
    auth = AuthHelper()
    audience_handler = AudienceHandler(auth)
    segment_manager = SegmentManager(auth)
    snapshot_exporter = SnapshotExporter(auth)

    while True:
        print("\n[bold]🎯 SEGMENTATION MENU[/bold]")
        print("────────────────────────────────────")
        print("1️⃣ List Audiences")
        print("2️⃣ Create 'All Profiles' Segment")
        print("3️⃣ Create New Audience (by PQL)")
        print("4️⃣ Delete Audience")
        print("5️⃣ View Audience by ID")
        print("6️⃣ Trigger Profile Snapshot Export")
        print("0️⃣ Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            audience_handler.list_audiences()
        elif choice == "2":
            segment_manager.create_all_profiles_segment()
        elif choice == "3":
            name = input("Audience Name: ")
            desc = input("Description: ")
            pql = input("PQL Expression: ")
            audience_handler.create_audience(name, desc, pql)
        elif choice == "4":
            aid = input("Audience ID to delete: ")
            audience_handler.delete_audience(aid)
        elif choice == "5":
            aid = input("Audience ID to view: ")
            audience_handler.get_audience_by_id(aid)
        elif choice == "6":
            snapshot_exporter.trigger_snapshot()
        elif choice == "0":
            print("[cyan]🔙 Returning to Main Menu...[/cyan]")
            break
        else:
            print("[red]❌ Invalid option. Try again.[/red]")
