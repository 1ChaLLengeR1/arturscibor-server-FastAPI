from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from DataBase.db import Base
import uuid


class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    login = Column(String)
    password = Column(String)
    type = Column(String)

    class Config:
        orm_mode = True


class CurriculumVitae(Base):
    __tablename__ = "curriculumvitae"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    path = Column(String)
    link = Column(String)

    class Config:
        orm_mode = True


class Jobs(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, server_default='uuid_generate_v4()')
    name = Column(String)

    class Config:
        orm_mode = True


class Information(Base):
    __tablename__ = "informationme"

    id = Column(String, primary_key=True, server_default='uuid_generate_v4()')
    information = Column(String)

    class Config:
        orm_mode = True


class ImagesMe(Base):
    __tablename__ = "imagesme"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    path = Column(String)
    link = Column(String)

    class Config:
        orm_mode = True


class AboutMe(Base):
    __tablename__ = "aboutme"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    job = Column(String)
    information = Column(String)
    path_image = Column(String)
    link_image = Column(String)

    class Config:
        orm_mode = True


class ReadMore(Base):
    __tablename__ = "readmore"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    information = Column(String)
    numeric = Column(Integer)

    class Config:
        orm_mode = True


class Tools(Base):
    __tablename__ = "tools"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    information = Column(String)
    progress = Column(String)
    numeric = Column(String)
    link = Column(String)
    path_image = Column(String)
    link_image = Column(String)

    class Config:
        orm_mode = True


class Projects(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name_project = Column(String)
    short_description = Column(String)
    file_path = Column(String)
    file_link = Column(String)
    completion_data = Column(DateTime, default=datetime.now())
    project_number = Column(Integer)
    level_advanced = Column(String)
    description = Column(String)
    link_page = Column(String)

    class Config:
        orm_mode = True


class FileProjects(Base):
    __tablename__ = "filesproject"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    id_project = Column(String)
    name = Column(String)
    path = Column(String)
    link = Column(String)

    class Config:
        orm_mode = True


class ImagesProjects(Base):
    __tablename__ = "imagesproject"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    id_project = Column(String)
    name = Column(String)
    path = Column(String)
    link = Column(String)
    type = Column(String)

    class Config:
        orm_mode = True


class TechnologiesProject(Base):
    __tablename__ = "technologiesproject"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    id_project = Column(String)
    name = Column(String)

    class Config:
        orm_mode = True


class Contact(Base):
    __tablename__ = "contact"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String)
    description = Column(String)

    class Config:
        orm_mode = True


class ImagesMessage(Base):
    __tablename__ = "imagesmessage"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    id_message = Column(String)
    path = Column(String)
    link = Column(String)

    class Config:
        orm_mode = True
