"""
EvoKB Memory Module - SQL-based structured memory

Ethical Usage:
- Only store data about people you have legitimate relationship with
- Don't store sensitive/personal info without consent
- Keep the database private (already in .gitignore)
- See PRIVACY.md for full guidelines
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    MetaData,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()
metadata = MetaData()

notes_people = Table(
    "notes_people",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id")),
    Column("person_id", Integer, ForeignKey("people.id")),
)

notes_projects = Table(
    "notes_projects",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id")),
    Column("project_id", Integer, ForeignKey("projects.id")),
)

notes_tags = Table(
    "notes_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id")),
    Column("tag", String(100)),
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    people = relationship("Person", secondary=notes_people, back_populates="notes")
    projects = relationship("Project", secondary=notes_projects, back_populates="notes")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "people": [p.name for p in self.people],
            "projects": [proj.name for proj in self.projects],
            "tags": self.get_tags(),
        }

    def get_tags(self) -> List[str]:
        return []


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    company = Column(String(200))
    role = Column(String(200))
    email = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)

    notes = relationship("Note", secondary=notes_people, back_populates="people")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "role": self.role,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.now)

    notes = relationship("Note", secondary=notes_projects, back_populates="projects")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))
    event_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.event_type,
            "date": self.event_date.isoformat() if self.event_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    rationale = Column(Text)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MemoryStore:
    def __init__(self, db_path: str = "evokb_memory.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_note(
        self,
        content: str,
        people: List[str] = None,
        projects: List[str] = None,
        tags: List[str] = None,
    ) -> Note:
        session = self.Session()
        try:
            note = Note(content=content)
            session.add(note)
            session.flush()

            if people:
                for name in people:
                    person = session.query(Person).filter(Person.name == name).first()
                    if not person:
                        person = Person(name=name)
                        session.add(person)
                    note.people.append(person)

            if projects:
                for name in projects:
                    proj = session.query(Project).filter(Project.name == name).first()
                    if not proj:
                        proj = Project(name=name)
                        session.add(proj)
                    note.projects.append(proj)

            session.commit()
            return note
        finally:
            session.close()

    def add_person(
        self, name: str, company: str = None, role: str = None, email: str = None
    ) -> Person:
        session = self.Session()
        try:
            person = Person(name=name, company=company, role=role, email=email)
            session.add(person)
            session.commit()
            return person
        finally:
            session.close()

    def add_project(
        self, name: str, description: str = None, status: str = "active"
    ) -> Project:
        session = self.Session()
        try:
            project = Project(name=name, description=description, status=status)
            session.add(project)
            session.commit()
            return project
        finally:
            session.close()

    def add_event(
        self,
        title: str,
        description: str = None,
        event_type: str = None,
        event_date: datetime = None,
    ) -> Event:
        session = self.Session()
        try:
            event = Event(
                title=title,
                description=description,
                event_type=event_type,
                event_date=event_date,
            )
            session.add(event)
            session.commit()
            return event
        finally:
            session.close()

    def add_decision(
        self, title: str, description: str = None, rationale: str = None
    ) -> Decision:
        session = self.Session()
        try:
            decision = Decision(
                title=title, description=description, rationale=rationale
            )
            session.add(decision)
            session.commit()
            return decision
        finally:
            session.close()

    def query_notes(
        self,
        query: str = None,
        person: str = None,
        project: str = None,
        tags: List[str] = None,
    ) -> List[Note]:
        session = self.Session()
        try:
            q = session.query(Note)
            if person:
                q = q.filter(Note.people.any(Person.name == person))
            if project:
                q = q.filter(Note.projects.any(Project.name == project))
            return q.all()
        finally:
            session.close()

    def get_person(self, name: str = None, id: int = None) -> Optional[Person]:
        session = self.Session()
        try:
            if id:
                return session.query(Person).filter(Person.id == id).first()
            return session.query(Person).filter(Person.name == name).first()
        finally:
            session.close()

    def get_project(self, name: str = None, id: int = None) -> Optional[Project]:
        session = self.Session()
        try:
            if id:
                return session.query(Project).filter(Project.id == id).first()
            return session.query(Project).filter(Project.name == name).first()
        finally:
            session.close()

    def get_all_notes(self) -> List[Note]:
        session = self.Session()
        try:
            return session.query(Note).all()
        finally:
            session.close()

    def get_all_people(self) -> List[Person]:
        session = self.Session()
        try:
            return session.query(Person).all()
        finally:
            session.close()

    def get_all_projects(self) -> List[Project]:
        session = self.Session()
        try:
            return session.query(Project).all()
        finally:
            session.close()

    def get_all_events(self) -> List[Event]:
        session = self.Session()
        try:
            return session.query(Event).all()
        finally:
            session.close()

    def get_all_decisions(self) -> List[Decision]:
        session = self.Session()
        try:
            return session.query(Decision).all()
        finally:
            session.close()
