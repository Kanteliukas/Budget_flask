from flask_login import UserMixin
from sqlalchemy import DateTime
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from budget import app, db 

class Vartotojas(db.Model, UserMixin):
    __tablename__ = "vartotojas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String(20), unique=True, nullable=False)
    el_pastas = db.Column(
        "El. pašto adresas", db.String(120), unique=True, nullable=False
    )
    nuotrauka = db.Column(db.String(20), nullable=False, default="default.jpg")
    slaptazodis = db.Column("Slaptažodis", db.String(60), unique=True, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return Vartotojas.query.get(user_id)


class Budget(db.Model):
    __tablename__ = "Budget"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column("Data", DateTime, default=datetime.now())
    entry = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(80), nullable=True)
    extra_information = db.Column(db.String(200), nullable=True)
    payment_option = db.Column(db.String(100), nullable=True)
    bought_goods_or_services = db.Column(db.String(200), nullable=True)
    vartotojas_id = db.Column(db.Integer, db.ForeignKey("vartotojas.id"))
    vartotojas = db.relationship("Vartotojas", lazy=True)

    def __init__(
        self,
        entry,
        amount,
        vartotojas_id,
        sender=None,
        extra_information=None,
        payment_option=None,
        bought_goods_or_services=None,
    ):
        self.entry = entry
        self.amount = amount
        self.sender = sender
        self.extra_information = extra_information
        self.payment_option = payment_option
        self.bought_goods_or_services = bought_goods_or_services
        self.vartotojas_id = vartotojas_id

    def __repr__(self):
        if self.entry == "Pajamos":
            return (
                f"{self.entry}: {self.amount}, {self.sender}, {self.extra_information};"
            )
        else:
            return f"{self.entry}: {self.amount}, {self.payment_option}, {self.bought_goods_or_services};"