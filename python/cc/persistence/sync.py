import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.orm import Session

from ..domain.models import Catalog as DomainCatalog
from .models import Base, Catalog, Course, Enrollment, Student, Subject

logger = logging.getLogger(__name__)


@event.listens_for(Base, "after_insert", propagate=True)
def _log_insert(_mapper: object, _connection: object, entity: object) -> None:
    logger.info("Created %s", entity)


def _sync_entities(session: Session, data: DomainCatalog) -> None:
    catalog = session.get(Catalog, 1) or Catalog(id=1)
    catalog.deleted_at = None
    session.add(catalog)

    for subject_data in data.subjects:
        subject = session.get(Subject, subject_data.id) or Subject(id=subject_data.id)
        subject.name = subject_data.name
        subject.deleted_at = None
        subject.catalog = catalog
        session.add(subject)

        for course_data in subject_data.courses:
            course = session.get(Course, course_data.id) or Course(id=course_data.id)
            course.name = course_data.name
            course.deleted_at = None
            course.subject = subject
            session.add(course)

            for student_data in course_data.students:
                student = session.get(Student, student_data.id) or Student(id=student_data.id)
                student.name = student_data.name
                student.deleted_at = None
                student.catalog = catalog
                session.add(student)

                enrollment = session.get(Enrollment, (course.id, student.id))
                if enrollment is None:
                    enrollment = Enrollment(course=course, student=student)
                enrollment.deleted_at = None
                session.add(enrollment)


def _ensure_schema(engine: object) -> None:
    # Add the soft-delete column to databases created before this field existed.
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if "deleted_at" not in {column["name"] for column in inspector.get_columns(table.name)}:
                connection.execute(
                    text(f'ALTER TABLE "{table.name}" ADD COLUMN deleted_at DATETIME')
                )


def _mark_missing(session: Session, data: DomainCatalog) -> list[object]:
    expected = {
        Subject: {subject.id for subject in data.subjects},
        Course: {
            course.id
            for subject in data.subjects
            for course in subject.courses
        },
        Student: {
            student.id
            for subject in data.subjects
            for course in subject.courses
            for student in course.students
        },
        Enrollment: {
            (course.id, student.id)
            for subject in data.subjects
            for course in subject.courses
            for student in course.students
        },
    }
    deleted = []
    for model, expected_ids in expected.items():
        for entity in session.scalars(select(model)).all():
            identity = inspect(entity).identity
            key = identity[0] if len(identity) == 1 else identity
            if key not in expected_ids and entity.deleted_at is None:
                entity.deleted_at = datetime.now(timezone.utc)
                deleted.append(entity)
    return deleted


def sync(data: DomainCatalog, database: str) -> None:
    # Upsert the source graph and mark omitted records as soft-deleted.
    engine = create_engine(f"sqlite:///{database}")
    try:
        _ensure_schema(engine)
        with Session(engine) as session:
            _sync_entities(session, data)
            deleted = _mark_missing(session, data)
            session.commit()
            for entity in deleted:
                logger.info("Deleted %s at %s", entity, entity.deleted_at)
    finally:
        engine.dispose()
