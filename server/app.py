from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_migrate import Migrate
from models import Cheese, Producer, db
from flask_restful import Api, Resource


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Producers(Resource):
    def get(self):
        producers = [producer.to_dict(rules=("-cheeses",)) for producer in Producer.query.all()]
        return make_response(
            producers,
            200
        )

api.add_resource(Producers, "/producers")


class ProducersByID(Resource):
    def get(self,id):
        producer = Producer.query.filter(Producer.id == id).first().to_dict()
        return make_response(
            producer,
            200
        )

api.add_resource(ProducersByID, "/producers/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
