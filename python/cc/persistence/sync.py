import logging

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import Session

from ..domain.models import Catalog as DomainCatalog
from .models import Base, Catalog, Course, Enrollment, Student, Subject

logger = logging.getLogger(__name__)


def _entity_label(entity: object) -> str:
    state = inspect(entity)
    identity = state.identity or tuple(
        getattr(entity, column.key) for column in state.mapper.primary_key
    )
    return f"{state.mapper.local_table.name}[{', '.join(map(str, identity))}]"


@event.listens_for(Base, "after_insert", propagate=True)
def _log_insert(_mapper: object, _connection: object, entity: object) -> None:
    logger.info("Created %s", _entity_label(entity))


@event.listens_for(Base, "after_delete", propagate=True)
def _log_delete(_mapper: object, _connection: object, entity: object) -> None:
    logger.info("Deleted %s", _entity_label(entity))


def to_orm_graph(data: DomainCatalog) -> Catalog:
    # Reuse one ORM student object for every occurrence of the same student ID.
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
    # Merge the complete graph so omitted YAML objects are removed by orphan cascades.
    engine = create_engine(f"sqlite:///{database}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.merge(to_orm_graph(data))
        session.commit()
