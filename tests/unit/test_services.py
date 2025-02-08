from datetime import date, timedelta
import adapters.repository as repository
import service_layer.services as services
import pytest
from service_layer import unit_of_work

today = date.today()
tomorrow = today + timedelta(days=1)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)
    with pytest.raises(
        services.InvalidSku, match="Недопустимый артикул NONEXISTENTSKU"
    ):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)

    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True


def test_prefers_warehouse_batches_to_shipments():
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, uow)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, uow)

    services.allocate("oref", "RETRO-CLOCK", 10, uow)

    in_stock_batch = uow.batches.get(reference="in-stock-batch")
    shipment_batch = uow.batches.get(reference="shipment-batch")

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_deallocate_decrements_available_quantity():
    uow = FakeUnitOfWork()
    # TODO: you'll need to implement the services.add_batch method
    services.add_batch("b1", "BLUE-PLINTH", 100, None, uow)
    services.allocate("o1", "BLUE-PLINTH", 10, uow)
    batch = uow.batches.get(reference="b1")
    assert batch.available_quantity == 90

    services.deallocate("b1", "o1", "BLUE-PLINTH", 10, uow)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity(): ...  #  TODO - check that we decrement the right sku


def test_trying_to_deallocate_unallocated_batch(): ...  #  TODO: should this error or pass silently? up to you.
