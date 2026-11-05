import logging
from pathlib import Path

import yaml

from ..domain.models import Catalog, Course, Student, Subject
from ..persistence.sync import sync

logger = logging.getLogger(__name__)


def load_yaml(path: Path) -> Catalog:
    # Treat a missing YAML body as an empty catalog.
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Catalog(
        subjects=[
            Subject(
                id=subject["id"],
                name=subject["name"],
                courses=[
                    Course(
                        id=course["id"],
                        name=course["name"],
                        students=[Student(**student) for student in course.get("students", [])],
                    )
                    for course in subject.get("courses", [])
                ],
            )
            for subject in raw.get("subjects", [])
        ]
    )


def sync_yaml(yaml_file: Path, database: str) -> None:
    # Convert the complete source document before handing it to persistence.
    logger.info("Synchronizing %s -> %s", yaml_file, database)
    sync(load_yaml(yaml_file), database)
