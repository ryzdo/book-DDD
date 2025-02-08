from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config
import domain.model as model
import adapters.orm as orm
import service_layer.services as services
from datetime import datetime
from service_layer import unit_of_work

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"batchref": batchref}), 201


@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    services.deallocate(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return jsonify({"ok": True}), 200
