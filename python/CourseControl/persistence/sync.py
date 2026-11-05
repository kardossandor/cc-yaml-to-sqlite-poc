from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..domain.models import Catalog as DomainCatalog
from .models import Base, Catalog, Course, Enrollment, Student, Subject


def to_orm_graph(data: DomainCatalog) -> Catalog:
    students: dict[str, Student] = {}
    subjects: list[Subject] = []

    for subject_data in data.subjects:
        subject = Subject(id=subject_data.id, name=subject_data.name)
        subjects.append(subject)

        for course_data in subject_data.courses:
            course = Course(id=course_data.id, name=course_data.name)
            subject.courses.append(course)

            for student_data in course_data.students:
                students.setdefault(
                    student_data.id,
                    Student(id=student_data.id, name=student_data.name),
                )
                course.enrollments.append(
                    Enrollment(student=students[student_data.id])
                )

    return Catalog(id=1, subjects=subjects, students=list(students.values()))


def sync(data: DomainCatalog, database: str) -> None:
    engine = create_engine(f"sqlite:///{database}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.merge(to_orm_graph(data))
        session.commit()
