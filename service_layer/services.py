import domain.model as model
from adapters.repository import AbstractRepository
from domain.model import OrderLine
from typing import Optional
from datetime import date


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Недопустимый артикул {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session
):
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def deallocate(ref: str, line: OrderLine, repo: AbstractRepository, session) -> str:
    batch = repo.get(ref)
    batch.deallocate(line)
    session.commit()
    return ref
