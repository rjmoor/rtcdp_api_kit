# rtcdp_api_kit/main.py

from rtcdp.cli.main import launch_menu
import logging
from pathlib import Path

# --- Constants ---
BASE_DIR = Path(__file__).resolve().parent
MAIN_DIR = BASE_DIR / "rtcdp"
LOG_DIR = BASE_DIR / "logs"
DATASET_LOG_FILE = LOG_DIR / "main_entry.log"

# --- Setup Logging ---
def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists
    logging.basicConfig(
        filename=str(DATASET_LOG_FILE),
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging system initialized.")

# --- Main App Entry ---
def main():
    setup_logging()
    logging.info("Launching main menu...")
    launch_menu()
    logging.info("Main menu session ended.")

if __name__ == "__main__":
    main()
