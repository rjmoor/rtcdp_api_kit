# modules/segment_data/segment_manager.py

import time
import requests
from rtcdp.utils.auth_helper import AuthHelper
from api.modules.segment_data.merge_policy_utils import MergePolicyHelper
from rich import print

class SegmentManager:
    def __init__(self, auth_helper: AuthHelper):
        self.auth = auth_helper
        self.segment_jobs_url = self.auth.get_endpoint("segment_jobs")
        self.policy_helper = MergePolicyHelper(auth_helper)
        self.token = self.auth.get_access_token()
        self.base_url = self.auth.get_base_url()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.auth.get_api_key(),
            "x-gw-ims-org-id": self.auth.get_org_id(),
            "x-sandbox-name": self.auth.get_sandbox(),
            "Content-Type": "application/json"
        }
        self.segmentation_url = "https://platform.adobe.io/data/core/ups/segments"
        self.segment_definitions_url = "https://platform.adobe.io/data/core/ups/segment/definitions"
        self.segment_jobs_url = "https://platform.adobe.io/data/core/ups/segment/jobs"

    def create_segment_by_name(self):
        print("\n🆕 Create a New Segment")
        name = input("Enter segment name: ").strip()
        description = input("Enter description: ").strip()
        pql = input("Enter PQL expression: ").strip()

        merge_policies = self.policy_helper.get_merge_policies()
        if not merge_policies:
            print("❌ No merge policies available.")
            return

        print("\n🔀 Select a Merge Policy:")
        for i, policy in enumerate(merge_policies, 1):
            print(f"{i}. {policy['name']} (ID: {policy['id']})")

        selected_index = int(input("Select a merge policy number: ")) - 1
        selected_policy_id = merge_policies[selected_index]["id"]

        payload = {
            "name": name,
            "description": description,
            "expression": {
                "type": "PQL",
                "format": "pql/text",
                "value": pql
            },
            "mergePolicyId": selected_policy_id
        }

        response = requests.post(self.segment_jobs_url, headers=self.headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print(f"✅ Segment '{name}' created successfully.")
        else:
            print(f"❌ Failed to create segment: {response.status_code}")
            print(response.text)


        self.url = self.auth.get_endpoint("segment_definitions")

    def list_segments(self):
        print("\n📄 Retrieving available segments (with pagination)...")

        search_term = input("🔎 Enter segment name filter (leave blank to list all): ").strip().lower()
        segment_map = {}
        start = 0
        limit = 100
        max_pages = 100

        for _ in range(max_pages):
            full_url = f"{self.url}?start={start}&limit={limit}"
            print(f"🔄 Fetching segments {start} to {start + limit - 1}")
            response = requests.get(full_url, headers=self.headers)

            if response.status_code != 200:
                print(f"❌ Failed to retrieve segments: {response.status_code}")
                print(response.text)
                break

            segments = response.json().get("segments", [])
            if not segments:
                break

            for seg in segments:
                segment_map[seg["id"]] = seg

            start += limit
            time.sleep(0.2)

        all_segments = list(segment_map.values())
        filtered = [s for s in all_segments if search_term in s.get("name", "").lower()] if search_term else all_segments

        print(f"\n📦 Total Segments: {len(filtered)}\n")
        for i, seg in enumerate(filtered, 1):
            print(f"{i}. {seg['name']} (ID: {seg['id']})")


    def create_all_profiles_segment(self):
        payload = {
            "name": "All Profiles",
            "description": "Segment includes all profile records",
            "type": "SegmentDefinition",
            "expression": {
                "type": "PQL",
                "format": "pql/text",
                "value": "profile.person.name.first exists"
            },
            "schema": {
                "name": "_xdm.context.profile"
            }
        }

        try:
            response = requests.post(f"{self.base_url}/audiences", headers=self.headers, json=payload)
            response.raise_for_status()
            print("[green]✔ 'All Profiles' segment created successfully![/green]")
        except Exception as e:
            print(f"[red]❌ Failed to create segment: {e}[/red]")
            
            