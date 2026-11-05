import argparse
from pathlib import Path

from .config import DATABASE_PATH
from .service.sync import sync_yaml


def main() -> None:
    # Keep command-line parsing separate from the synchronization workflow.
    parser = argparse.ArgumentParser(description="Synchronize YAML into SQLite.")
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()
    sync_yaml(args.yaml_file, DATABASE_PATH)
    print(f"Synchronized {args.yaml_file} -> {DATABASE_PATH}")
