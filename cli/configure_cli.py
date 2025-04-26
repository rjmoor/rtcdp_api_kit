# cli/configure_cli.py

import json
import os
import requests
import subprocess
import logging
from rich import print
import time
from datetime import datetime, timedelta

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "configure_cli.log"),
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CREDENTIALS_PATH = os.path.join("config", "cit-credentials.json")

class ConfigurationManager:
    pass