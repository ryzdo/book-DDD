# pytest: disable=redefined-outer-name
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

# from orm import metadata  #  не поддерживается в SQLAlchemy 2.0
from orm import start_mappers, mapper_registry


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")

    # metadata.create_all(engine)  #  не поддерживается в SQLAlchemy 2.0
    mapper_registry.metadata.create_all(engine)

    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
