import requests
import time

class ListSegments:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        self.headers = self.auth.get_headers()
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
