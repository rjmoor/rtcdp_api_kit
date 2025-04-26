# rtcdp_api_kit/main.py

from cli.main_cli import launch_menu
import logging
import os

# Configure Logging
LOG_DIR = "logs"
DATASET_LOG = "main_entry.log"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f"{LOG_DIR}/{DATASET_LOG}",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    launch_menu()
    logging.info("The main menu has been launched")

if __name__ == "__main__":
    main()

