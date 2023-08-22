from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

class TimestampMixin:
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
     )

class Producer(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "producers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer)
    region = db.Column(db.String)
    operation_size = db.Column(db.String)
    image = db.Column(db.String)

    cheeses = db.relationship("Cheese", back_populates="producer", lazy=True, cascade="delete")

    serialize_rules = ("-cheeses.producer","-created_at", "-updated_at")

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
    price = db.Column(db.Float)
    image = db.Column(db.String)
    is_raw_milk = db.Column(db.Boolean)
    production_date = db.Column(db.DateTime)

    producer_id = db.Column(db.Integer, db.ForeignKey("producers.id"), nullable=False)

    serialize_rules = ("-producers.cheeses","-created_at", "-updated_at")


    @validates("production_date")
    def validate_production_date(self,key,date):
        production_date = datetime.strptime(date, "%Y-%m-%d")
        if production_date >= datetime.now():
            raise ValueError("Invalid date, msut be in the past")
        return production_date
    
    @validates("price")
    def validate_price(self,key,price):
        if not 1.00 <= price <= 45.00:
            raise ValueError("Price must be between 1.00 and 45.00")
        return price
    
    def __repr__(self):
        return f"<Cheese {self.id}>"
