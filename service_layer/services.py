import domain.model as model
from service_layer import unit_of_work
from typing import Optional
from datetime import date


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    orderid: str,
    sku: str,
    qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = model.OrderLine(orderid, sku, qty)

    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku, batches):
            raise InvalidSku(f"Недопустимый артикул {sku}")
        batchref = model.allocate(line, batches)
        uow.commit()
    return batchref


def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def deallocate(
    ref: str,
    orderid: str,
    sku: str,
    qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = model.OrderLine(orderid, sku, qty)

    with uow:
        batch = uow.batches.get(ref)
        batch.deallocate(line)
        uow.commit()
    return ref
