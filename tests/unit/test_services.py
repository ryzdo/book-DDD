from datetime import date, timedelta
import adapters.repository as repository
import domain.model as model
import service_layer.services as services
import pytest


today = date.today()
tomorrow = today + timedelta(days=1)


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)
    with pytest.raises(
        services.InvalidSku, match="Недопустимый артикул NONEXISTENTSKU"
    ):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


def test_prefers_warehouse_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, repo, session)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, repo, session)

    services.allocate("oref", "RETRO-CLOCK", 10, repo, session)

    in_stock_batch = repo.get(reference="in-stock-batch")
    shipment_batch = repo.get(reference="shipment-batch")

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    # TODO: you'll need to implement the services.add_batch method
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    services.allocate("o1", "BLUE-PLINTH", 10, repo, session)
    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90

    services.deallocate("b1", "o1", "BLUE-PLINTH", 10, repo, session)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity(): ...  #  TODO - check that we decrement the right sku


def test_trying_to_deallocate_unallocated_batch(): ...  #  TODO: should this error or pass silently? up to you.
