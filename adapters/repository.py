from sqlalchemy.orm import Session
from sqlalchemy import select
import abc
import domain.model as model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[model.Batch]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        # return self.session.query(model.Batch).filter_by(reference).one()
        return self.session.scalars(
            select(model.Batch).where(model.Batch.reference == reference)
        ).one()

    def list(self):
        return self.session.query(model.Batch).all()
