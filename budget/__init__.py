import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    current_user
)
from flask_mail import Mail




basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = "4654f5dfadsrfasdr54e6rae"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "biudzetas.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
db.create_all()

from budget.models import Vartotojas, Budget
from budget.models import *
migrate = Migrate(app, db, render_as_batch=True)


bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = "prisijungti"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(vartotojo_id):
    db.create_all()
    return Vartotojas.query.get(int(vartotojo_id))

class ManoModelView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_authenticated and current_user.el_pastas == "as@example.com"
        )

from budget.routes import *
admin = Admin(app)
admin.add_view(ManoModelView(Vartotojas, db.session))
admin.add_view(ModelView(Budget, db.session))

from budget.email_settings import *
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = MAIL_USERNAME
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD

