import requests

class MergePolicyHelper:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        self.headers = self.auth.get_headers()
        self.url = self.auth.get_endpoint("merge_policies")

    def get_merge_policies(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code != 200:
            print(f"❌ Merge policy retrieval failed: {response.status_code}")
            return []

        return response.json().get("mergePolicies", [])
