import requests
import json
from modules.segment_data.merge_policy_utils import MergePolicyHelper

class CreateSegment:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        self.headers = self.auth.get_headers()
        self.segment_jobs_url = self.auth.get_endpoint("segment_jobs")
        self.policy_helper = MergePolicyHelper(auth_helper)

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
