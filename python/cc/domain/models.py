from dataclasses import dataclass


@dataclass
class Student:
    # A student can be enrolled in multiple courses within the catalog.
    id: str
    name: str


@dataclass
class Course:
    id: str
    name: str
    # Enrollments are kept on the course side in the input graph.
    students: list[Student]


@dataclass
class Subject:
    id: str
    name: str
    courses: list[Course]


@dataclass
class Catalog:
    # The domain model mirrors the hierarchy represented by the YAML document.
    subjects: list[Subject]
