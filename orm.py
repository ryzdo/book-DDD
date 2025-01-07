from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey

# from sqlalchemy.orm import mapper  #  не поддерживается в SQLAlchemy 2.0
from sqlalchemy.orm import registry, relationship

import model


# metadata = MetaData()  #  не поддерживается в SQLAlchemy 2.0
mapper_registry = registry()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderid", String(255)),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
)


batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)


allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    # lines_mapper = mapper(model.OrderLine, order_lines)  #  не поддерживается в SQLAlchemy 2.0
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)

    mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
