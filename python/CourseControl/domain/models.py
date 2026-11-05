from dataclasses import dataclass


@dataclass
class Student:
    id: str
    name: str


@dataclass
class Course:
    id: str
    name: str
    students: list[Student]


@dataclass
class Subject:
    id: str
    name: str
    courses: list[Course]


@dataclass
class Catalog:
    subjects: list[Subject]
