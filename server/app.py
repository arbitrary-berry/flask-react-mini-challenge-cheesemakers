from datetime import datetime

from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import Cheese, Producer, db
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


# @app.route("/")
# def index():
#     response = make_response({"message": "Hello Fromagers!"}, 200)
#     return response


class Producers(Resource):
    def get(self):
        producers = [
            producer.to_dict(rules=("-cheeses",)) for producer in Producer.query.all()
        ]
        response = make_response(jsonify(producers), 200)
        return response


class ProducersById(Resource):
    def get(self, id):
        producer = Producer.query.get_or_404(id)
        response = make_response(jsonify(producer.to_dict()), 200)
        return response

    def delete(self, id):
        producer = Producer.query.get_or_404(id)
        db.session.delete(producer)
        db.session.commit()
        response = make_response("", 204)
        return response


class Cheeses(Resource):
    def post(self):
        data = request.get_json()
        try:
            cheese = Cheese(**data)
        except ValueError as e:
            response = make_response(jsonify({"error": e.args}), 422)
            return response

        db.session.add(cheese)
        db.session.commit()
        response = make_response(
            jsonify(
                cheese.to_dict(
                    rules=(
                        "-producer.founding_year",
                        "-producer.region",
                        "-producer.operation_size",
                        "-producer.image",
                        "-producer.id",
                    )
                )
            ),
            201,
        )
        return response


class CheesesById(Resource):
    def patch(self, id):
        cheese = Cheese.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items():
            if key == "production_date":
                value = datetime.strptime(value, "%Y-%m-%d")
            setattr(cheese, key, value)
        db.session.commit()
        response = make_response(jsonify(cheese.to_dict(rules=("-producer",))), 200)
        return response

    def delete(self, id):
        cheese = Cheese.query.get_or_404(id)
        db.session.delete(cheese)
        db.session.commit()
        response = make_response("", 204)
        return response


api.add_resource(Producers, "/producers")
api.add_resource(ProducersById, "/producers/<int:id>")
api.add_resource(Cheeses, "/cheeses")
api.add_resource(CheesesById, "/cheeses/<int:id>")


@app.errorhandler(NotFound)
def handle_not_found(error):
    return make_response(jsonify({"error": "Resource not found"}), 404)


if __name__ == "__main__":
    app.run(port=5555, debug=True)