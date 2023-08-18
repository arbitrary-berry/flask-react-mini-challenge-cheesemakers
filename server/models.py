from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()


class Producer(db.Model, SerializerMixin):
    __tablename__ = "producers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer)
    region = db.Column(db.String)
    operation_size = db.Column(db.String)
    image = db.Column(db.String)

    cheeses = db.relationship("Cheese", back_populates="producer", cascade="all, delete-orphan")

    serialize_rules = ("-cheeses.producer",)

    @validates("founding_year")
    def validate_founding_year(self,key,year):
        if year < 1900 or year > 2023:
            raise ValueError("Invalid founding year")
        return year

    @validates("operation_size")
    def validate_operation_size(self,key,size):
        if not size in ("small", "medium", "large", "family", "corporate"):
            raise ValueError("Invalid operation size")
        return size

            

    def __repr__(self):
        return f"<Producer {self.id}>"


class Cheese(db.Model, SerializerMixin):
    __tablename__ = "cheeses"

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String)
    price = db.Column(db.Integer)
    image = db.Column(db.String)
    is_raw_milk = db.Column(db.Boolean)
    production_date = db.Column(db.DateTime)

    producer = db.relationship("Producer", back_populates="cheeses")
    producer_id = db.Column(db.Integer, db.ForeignKey("producers.id"))

    serialize_rules = ("-producer.cheeses",)


    @validates("production_date")
    def validate_production_date(self,key,date):
        if date > datetime.now().date():
            raise ValueError("Invalid date")
        return date
    
    @validates("price")
    def validte_price(self,key,price):
        if price < 1 or price > 45.00:
            raise ValueError("Invalid price 1-45")
        return price
    
    def __repr__(self):
        return f"<Cheese {self.id}>"
