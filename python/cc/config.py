import os


# Use a local SQLite file unless the deployment provides another path.
DATABASE_PATH = os.getenv("CC_DATABASE", "data.sqlite")

# Select "console" or "file" as the logging destination.
LOG_DESTINATION = os.getenv("CC_LOG_DESTINATION", "file")
LOG_FILE = os.getenv("CC_LOG_FILE", "course-control.log")
