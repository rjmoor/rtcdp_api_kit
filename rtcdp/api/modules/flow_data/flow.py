import json
import requests
import logging
import os
import subprocess

# Configure logging
logging.basicConfig(
    filename="source_connection.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SourceConnectionAPI:
    """Handles Source Connection operations in Adobe Experience Platform (AEP)."""

    def __init__(self, credentials_file, environment):
        """
        Initialize the Source Connection API instance.
        
        Args:
            credentials_file (str): Path to the credentials JSON file.
            environment (dict): Selected environment configuration.
        """
        self.credentials_file = credentials_file
        self.credentials = self.load_credentials()
        self.base_url = self.credentials["base_url"]
        self.api_key = self.credentials["api_key"]
        self.org_id = self.credentials["org_id"]
        self.environment = environment

    def load_credentials(self):
        """Load API credentials from a JSON file."""
        try:
            with open(self.credentials_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"❌ Error loading credentials: {e}")
            raise

    def refresh_token(self):
        """Run ims.token_refresh.py to refresh the OAuth token."""
        try:
            print("🔄 Refreshing OAuth Token...")
            subprocess.run(["python3", "../ims.token_refresh.py"], check=True)
            logging.info("✔ Token refreshed successfully.")
            print("✔ Token refreshed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Failed to refresh token: {e}")
            raise RuntimeError("❌ Token refresh failed. Check logs for details.")

    def get_access_token(self):
        """Retrieve a valid access token, refreshing it if necessary."""
        access_token = self.credentials.get("access_token")

        if not access_token:
            logging.warning("⚠️ No access token found. Attempting to refresh...")
            self.refresh_token()
            self.credentials = self.load_credentials()
            return self.credentials.get("access_token")

        return access_token

    def create_source_connection(self):
        """Create a new Source Connection in AEP."""
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/connections"

            name = input("Enter connection name: ")
            description = input("Enter connection description: ")

            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-api-key": self.api_key,
                "x-gw-ims-org-id": self.org_id,
                "x-sandbox-name": self.environment["sandbox_id"],
                "Content-Type": "application/json"
            }

            payload = {
                "name": name,
                "description": description,
                "connectionSpec": {
                    "id": "bc7b00d6-623a-4dfc-9fdb-f1240aeadaeb",
                    "version": "1.0"
                },
                "auth": {
                    "specName": "Streaming Connection",
                    "params": {
                        "dataType": "xdm"
                    }
                }
            }

            logging.info(f"🚀 Creating Source Connection: {name}")
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                logging.info("✔ Source Connection created successfully.")
                print("✔ Source Connection Created Successfully!")
                return response.json()
            else:
                logging.error(f"❌ Error creating source connection: {response.text}")
                print(f"❌ Error: {response.text}")

        except Exception as e:
            logging.error(f"❌ Error creating Source Connection: {e}")
            raise

    def list_connections(self):
        """Retrieve and display all existing Source Connections."""
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/flowservice/sourceConnections"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-api-key": self.api_key,
                "x-gw-ims-org-id": self.org_id,
                "x-sandbox-name": self.environment["sandbox_id"],
                "Content-Type": "application/json"
            }

            logging.info("🔍 Fetching all Source Connections...")
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                connections = response.json().get('items', [])
                if not connections:
                    print("⚠️ No source connections found.")
                    return []
                
                print("\n🔍 **Existing Source Connections:**")
                for i, conn in enumerate(connections, start=1):
                    print(f"{i}. 🆔 {conn['id']} | 📌 {conn['name']} | Status: {conn.get('state', 'unknown')}")
                return connections

            elif response.status_code == 401:
                logging.warning("⚠️ OAuth token expired. Refreshing and retrying...")
                print("⚠️ OAuth token expired. Refreshing and retrying...")
                self.refresh_token()
                return self.list_connections()

            elif response.status_code == 404:
                logging.error("❌ API endpoint not found. Check the base URL.")
                print("❌ API endpoint not found. Ensure the base URL is correct.")

            else:
                logging.error(f"❌ Failed to fetch source connections: {response.text}")
                print(f"❌ Error retrieving source connections. Status: {response.status_code}")

        except Exception as e:
            logging.error(f"❌ Error fetching source connections: {e}")
            print(f"❌ An error occurred. See logs for details.")

    def delete_connection(self):
        """
        Delete a selected Source Connection from AEP.

        Prompts user to select an existing connection for deletion.
        """
        print("\n📌 Retrieving available source connections...")
        connections = self.list_connections()

        if not connections:
            print("⚠️ No connections available to delete.")
            return

        print("\n🔍 **Select a Source Connection to Delete:**")
        for i, conn in enumerate(connections, start=1):
            print(f"{i}. 🆔 {conn['id']} | 📌 {conn['name']}")

        try:
            selection = int(input("\nEnter the number of the connection to delete: ")) - 1
            if selection < 0 or selection >= len(connections):
                print("❌ Invalid selection. Returning to main menu.")
                return

            selected_conn_id = connections[selection]['id']
            confirm = input(f"Are you sure you want to delete connection {selected_conn_id}? (yes/no): ")
            if confirm.lower() != "yes":
                print("❌ Deletion canceled. Returning to main menu.")
                return

            access_token = self.get_access_token()
            url = f"{self.base_url}/flowservice/connections/{selected_conn_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-api-key": self.api_key,
                "x-gw-ims-org-id": self.org_id,
                "x-sandbox-name": self.environment["sandbox_id"]
            }

            logging.info(f"🗑 Deleting connection: {selected_conn_id}")
            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                logging.info(f"✔ Connection {selected_conn_id} deleted successfully.")
                print("✔ Connection Deleted Successfully!")
            else:
                logging.error("❌ Error: %s", response.text)
                print(f"❌ Error: {response.text}")

        except Exception as e:
            logging.error(f"❌ Error deleting source connection: {e}")
            print("❌ An error occurred. See logs for details.")

    def test_connection(self):
        """
        Test if a selected Source Connection is active.
        
        - Prompts user to select a connection.
        - Sends an API request to check connection status.
        - Provides success or failure feedback.
        """
        print("\n📌 Retrieving available source connections...")
        connections = self.list_connections()

        if not connections:
            print("⚠️ No connections available to test.")
            return

        print("\n🔍 **Select a Source Connection to Test:**")
        for i, conn in enumerate(connections, start=1):
            print(f"{i}. 🆔 {conn['id']} | 📌 {conn['name']}")

        try:
            selection = int(input("\nEnter the number of the connection to test: ")) - 1
            if selection < 0 or selection >= len(connections):
                print("❌ Invalid selection. Returning to main menu.")
                return

            selected_conn_id = connections[selection]['id']
            selected_conn_name = connections[selection]['name']

            print(f"🔄 Testing connection: {selected_conn_name} ({selected_conn_id})...")

            access_token = self.get_access_token()
            url = f"{self.base_url}/connections/{selected_conn_id}/test"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-api-key": self.api_key,
                "x-gw-ims-org-id": self.org_id,
                "x-sandbox-name": self.environment["sandbox_id"]
            }

            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                print(f"✅ Connection '{selected_conn_name}' is active and working!")
                logging.info(f"✔ Connection {selected_conn_name} ({selected_conn_id}) is active.")
            elif response.status_code == 400:
                print(f"⚠️ Connection '{selected_conn_name}' has issues. Check logs for details.")
                logging.warning(f"⚠️ Connection {selected_conn_name} returned 400: {response.text}")
            elif response.status_code == 404:
                print(f"❌ Connection '{selected_conn_name}' not found.")
                logging.error(f"❌ Connection {selected_conn_name} ({selected_conn_id}) not found (404).")
            elif response.status_code == 500:
                print(f"❌ Connection '{selected_conn_name}' test failed due to a server error.")
                logging.error(f"❌ Server error while testing connection {selected_conn_name}.")
            else:
                print(f"❌ Unknown error while testing connection '{selected_conn_name}'. See logs.")
                logging.error(f"❌ Error testing connection {selected_conn_name}: {response.text}")

        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except Exception as e:
            logging.error(f"❌ Error testing connection: {e}")
            print(f"❌ An error occurred. See logs for details.")

# ✅ **Main Menu**
def main_menu():
    """
    Terminal menu for Source Connection API management.
    """
    credentials_path = os.path.join("CREDS", "rol_credentials.json")

    with open(credentials_path, "r") as file:
        credentials = json.load(file)

    environments = credentials.get("environments", [])

    print("\n🌎 Select Environment:")
    for index, env in enumerate(environments, start=1):
        print(f"{index}. {env['name']}")
    
    try:
        env_choice = int(input("Select an environment (number): ")) - 1
        if env_choice < 0 or env_choice >= len(environments):
            print("❌ Invalid environment selection. Exiting.")
            return
    except ValueError:
        print("❌ Invalid input. Exiting.")
        return

    selected_environment = environments[env_choice]
    api = SourceConnectionAPI(credentials_path, selected_environment)

    while True:
        print("\n🔹 **Source Connection API Applet**")
        print("1️⃣ Create a Source Connection")
        print("2️⃣ View Existing Connections")
        print("3️⃣ Delete a Connection")
        print("4️⃣ View Streaming Endpoint URL for a Connection")
        print("5️⃣ Test an Existing Connection")
        print("6️⃣ Create a Target Dataset and Link to a Connection")
        print("7️⃣ Create a Dataflow")
        print("8️⃣ Post Test Data")
        print("9️⃣ Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            api.create_source_connection()
        elif choice == "2":
            api.list_connections()
        elif choice == "3":
            print("🚧 Delete function not implemented yet.")
        elif choice == "4":
            print("🚧 View Streaming Endpoint function not implemented yet.")
        elif choice == "5":
            api.test_connection()
        elif choice == "6":
            print("🚧 Create Target Dataset function not implemented yet.")
        elif choice == "7":
            print("🚧 Create Dataflow function not implemented yet.")
        elif choice == "8":
            print("🚧 Post Test Data function not implemented yet.")
        elif choice == "9":
            print("👋 Exiting Source Connection API. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
