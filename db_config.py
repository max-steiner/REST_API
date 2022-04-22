from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from configparser import ConfigParser


config = ConfigParser()
config.read("c:\\Users\\User\\PycharmProjects\\REST_API\\config.conf")
connection_string = config["db"]["connection_string"]
Base = declarative_base()
engine = create_engine(connection_string, echo=True)


def create_all_entities():
    Base.metadata.create_all(engine)


Session = sessionmaker()

local_session = Session(bind=engine)
