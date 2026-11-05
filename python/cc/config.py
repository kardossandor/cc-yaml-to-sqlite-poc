import os


# Use a local SQLite file unless the deployment provides another path.
DATABASE_PATH = os.getenv("CC_DATABASE", "data.sqlite")
