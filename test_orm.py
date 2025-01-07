import model

# from sqlalchemy.sql import text
from sqlalchemy import select, text


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty) VALUES "
            '("order1", "RED-CHAIR", 12),'
            '("order1", "RED-TABLE", 13),'
            '("order2", "BLUE-LIPSTICK", 14)'
        )
    )
    expected = [
        model.OrderLine(orderid="order1", sku="RED-CHAIR", qty=12),
        model.OrderLine(orderid="order1", sku="RED-TABLE", qty=13),
        model.OrderLine(orderid="order2", sku="BLUE-LIPSTICK", qty=14),
    ]

    assert session.execute(select(model.OrderLine)).scalars().all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine(orderid="order1", sku="DECORATIVE-WIDGET", qty=12)
    session.add(new_line)
    session.commit()
    rows = list(session.execute(text('SELECT orderid, sku, qty FROM "order_lines"')))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
