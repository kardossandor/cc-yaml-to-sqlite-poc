from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, inspect
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    # Shared declarative base for all database models.
    def __str__(self) -> str:
        state = inspect(self)
        identity = state.identity or tuple(
            getattr(self, column.key) for column in state.mapper.primary_key
        )
        return f"{state.mapper.local_table.name}[{', '.join(map(str, identity))}]"


class Catalog(Base):
    __tablename__ = "catalogs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Subjects and students belong to the single catalog root.
    subjects: Mapped[list[Subject]] = relationship(
        cascade="all, delete-orphan", back_populates="catalog"
    )
    students: Mapped[list[Student]] = relationship(
        cascade="all, delete-orphan", back_populates="catalog"
    )


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalogs.id"))
    name: Mapped[str] = mapped_column(String)
    catalog: Mapped[Catalog] = relationship(back_populates="subjects")
    courses: Mapped[list[Course]] = relationship(
        cascade="all, delete-orphan", back_populates="subject"
    )


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"))
    name: Mapped[str] = mapped_column(String)
    subject: Mapped[Subject] = relationship(back_populates="courses")
    enrollments: Mapped[list[Enrollment]] = relationship(
        cascade="all, delete-orphan", back_populates="course"
    )
    # Expose related students without duplicating the many-to-many mapping.
    students = association_proxy("enrollments", "student")


class Student(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalogs.id"))
    name: Mapped[str] = mapped_column(String)
    catalog: Mapped[Catalog] = relationship(back_populates="students")
    enrollments: Mapped[list[Enrollment]] = relationship(
        cascade="all", back_populates="student"
    )
    courses = association_proxy("enrollments", "course")


class Enrollment(Base):
    __tablename__ = "enrollments"
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), primary_key=True)
    # The composite key prevents the same student-course link from being stored twice.
    course: Mapped[Course] = relationship(back_populates="enrollments")
    student: Mapped[Student] = relationship(back_populates="enrollments")
