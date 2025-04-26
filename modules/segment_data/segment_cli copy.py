import requests
import json
import sys
import time
from rich import print

class SegmentHandler:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        self.access_token = self.auth.get_access_token()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'x-api-key': self.auth.credentials["api_key"],
            'x-gw-ims-org-id': self.auth.credentials["org_id"],
            'x-sandbox-name': self.auth.credentials.get("sandbox", "dev"),
            'Content-Type': 'application/json'
        }
        self.segmentation_url = "https://platform.adobe.io/data/core/ups/segments"
        self.segment_definitions_url = "https://platform.adobe.io/data/core/ups/segment/definitions"
        self.segment_jobs_url = "https://platform.adobe.io/data/core/ups/segment/jobs"

    def list_segments(self):
        print("\n📄 Retrieving available segments (with pagination)...")

        search_term = input("🔎 Enter segment name filter (leave blank to list all): ").strip().lower()
        segment_map = {}  # Use dict to deduplicate by segment ID
        start = 0
        limit = 100
        max_pages = 100

        for _ in range(max_pages):
            url = f"{self.segment_definitions_url}?start={start}&limit={limit}"
            print(f"🔄 Fetching segments {start} to {start + limit - 1}")
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                print(f"❌ Failed to retrieve segments (start={start}): {response.status_code}")
                print(response.text)
                break

            segments = response.json().get("segments", [])
            if not segments:
                print("✅ No more segments found.")
                break

            # Add each segment to the dictionary using segment ID as key
            for seg in segments:
                segment_map[seg["id"]] = seg

            start += limit
            time.sleep(0.2)

        all_segments = list(segment_map.values())
        print(f"\n📦 Total Unique Segments Retrieved: {len(all_segments)}")

        # Apply search filter if needed
        if search_term:
            filtered_segments = [
                seg for seg in all_segments if search_term in seg.get("name", "").lower()
            ]
            print(f"🔎 Matching Segments: {len(filtered_segments)}\n")
        else:
            filtered_segments = all_segments

        for i, seg in enumerate(filtered_segments, 1):
            print(f"{i}. {seg['name']} (ID: {seg['id']})")

        return filtered_segments

    def create_all_profiles_segment(self):
        print("\n🆕 Creating a new 'All Profiles' segment...")
        segment_body = {
            "name": "All Profiles Segment",
            "description": "Segment that includes all profiles for export purposes",
            "expression": {
                "type": "PQL",
                "format": "pql/text",
                "value": "identityMap['ECID'].namespace != null"  # a catch-all condition
            },
            "mergePolicyId": self.auth.merge_policy_id
        }

        url = self.segment_jobs_url
        response = requests.post(url, headers=self.headers, data=json.dumps(segment_body))

        if response.status_code == 201:
            segment = response.json()
            print(f"✅ Segment created: {segment['name']} (ID: {segment['id']})")
            return segment
        else:
            print(f"❌ Failed to create segment: {response.status_code}")
            print(response.text)
            return None

    def run_cli(self):
        while True:
            print("\n=== Segment Handler Menu ===")
            print("1️⃣ - List existing segments")
            print("2️⃣ - Filter by Name")
            print("3️⃣ - Create 'All Profiles' segment")
            print("0️⃣ - Exit")
            
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.list_segments()
            elif choice == "2":
                print("This is for the names")
                break
            elif choice == "3":
                self.create_all_profiles_segment()
            elif choice == "0":
                print("👋 Exiting Segment Handler.")
                break
            else:
                print("Invalid choice. Please select a valid option.")

