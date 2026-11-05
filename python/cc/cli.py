import argparse
import logging
from pathlib import Path

from .config import DATABASE_PATH, LOG_DESTINATION, LOG_FILE
from .service.sync import sync_yaml


def main() -> None:
    # Keep command-line parsing separate from the synchronization workflow.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE)
            if LOG_DESTINATION == "file"
            else logging.StreamHandler()
        ],
    )
    parser = argparse.ArgumentParser(description="Synchronize YAML into SQLite.")
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()
    sync_yaml(args.yaml_file, DATABASE_PATH)
    logging.info("Synchronized %s -> %s", args.yaml_file, DATABASE_PATH)
