import requests
import json
import logging


class AEPClient:
    """
    A class to interact with Adobe Experience Platform (AEP) APIs, allowing for retrieving audience data
    and handling multiple environments specified in a credentials file.

    Attributes:
        credentials (dict): A dictionary loaded from the credentials JSON file.
        access_token (str): The access token for API authentication.
        api_key (str): The API key for API access.
        org_id (str): The Adobe organization ID.
        base_url (str): The base URL for Adobe APIs.
    """

    def __init__(self, credentials_file="cit-credentials.json"):
        """
        Initializes the AEPClient with credentials loaded from a file and sets up logging.

        Args:
            credentials_file (str): Path to the credentials JSON file.
        """
        self.credentials = self._load_credentials(credentials_file)
        self.access_token = self.credentials["access_token"]
        self.api_key = self.credentials["api_key"]
        self.org_id = self.credentials["org_id"]
        self.base_url = self.credentials["base_url"]
        self.environments = self.credentials["environments"]

        logging.basicConfig(
            filename="aep_client.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("AEPClient initialized.")

    def _load_credentials(self, file_path):
        """
        Loads credentials from a JSON file.

        Args:
            file_path (str): Path to the credentials JSON file.

        Returns:
            dict: Loaded credentials.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        try:
            with open(file_path, "r") as file:
                logging.info(f"Loading credentials from {file_path}.")
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"Credentials file {file_path} not found.")
            raise
        except json.JSONDecodeError:
            logging.error("Error decoding credentials.json file. Ensure it is valid JSON.")
            raise

    def get_audience(self, audience_id, environment_name="Production"):
        """
        Retrieves audience data from the AEP API for a given audience ID and environment.

        Args:
            audience_id (str): The ID of the audience to retrieve.
            environment_name (str): The environment to use (e.g., "Production").

        Returns:
            dict: Audience data if successful.

        Raises:
            ValueError: If the specified environment is not found in the credentials file.
            requests.exceptions.RequestException: If an API request fails.
        """
        environment = next(
            (env for env in self.environments if env["name"] == environment_name), None
        )
        if not environment:
            logging.error(f"Environment '{environment_name}' not found.")
            raise ValueError(f"Environment '{environment_name}' not found in credentials.")

        sandbox_id = environment["sandbox_id"]
        url = f"{self.base_url}/data/core/ups/audiences/{audience_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "x-sandbox-name": sandbox_id,
            "Content-Type": "application/json"
        }

        try:
            logging.info(f"Fetching audience {audience_id} from environment '{environment_name}'.")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logging.info(f"Audience {audience_id} retrieved successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch audience {audience_id}: {e}")
            raise

    def list_environments(self):
        """
        Lists all environments specified in the credentials file.

        Returns:
            list: A list of environment names.
        """
        return [env["name"] for env in self.environments]


# Example Usage
if __name__ == "__main__":
    try:
        # Initialize the AEPClient
        client = AEPClient("cit-credentials.json")

        # List available environments
        print("Available Environments:", client.list_environments())

        # Fetch audience data
        audience_id = "adaa69de-2039-4ffd-84ff-0d2a4a978e95"
        environment_name = "Development"
        audience_data = client.get_audience(audience_id, environment_name)
        print("Audience Data:", json.dumps(audience_data, indent=4))

    except Exception as e:
        print(f"Error: {e}")
