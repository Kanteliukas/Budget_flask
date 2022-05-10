import os
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required
import secrets
from PIL import Image
from flask_mail import Message
from budget import forms, db, app, bcrypt, mail
from budget.models import Vartotojas, Budget
from budget.budget_functions.input_validation import validate_inputs
from budget.budget_functions.print_entries import get_entries
from budget.budget_functions.get_balance import get_balance
from budget.budget_functions.add_entry import add_new_entry


@app.route("/admin")
@login_required
def admin():
    return redirect(url_for(admin))


@app.route("/registruotis", methods=["GET", "POST"])
def registruotis():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.RegistracijosForma()
    if form.validate_on_submit():
        koduotas_slaptazodis = bcrypt.generate_password_hash(
            form.slaptazodis.data
        ).decode("utf-8")
        vartotojas = Vartotojas(
            vardas=form.vardas.data,
            el_pastas=form.el_pastas.data,
            slaptazodis=koduotas_slaptazodis,
        )
        db.session.add(vartotojas)
        db.session.commit()
        flash("Sėkmingai prisiregistravote! Galite prisijungti", "success")
        return redirect(url_for("index"))
    return render_template("registruotis.html", title="Register", form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Slaptažodžio atnaujinimo užklausa",
        sender="el@pastas.lt",
        recipients=[user.el_pastas],
    )
    msg.body = f"""Norėdami atnaujinti slaptažodį, paspauskite nuorodą:
    {url_for('reset_token', token=token, _external=True)}
    Jei jūs nedarėte šios užklausos, nieko nedarykite ir slaptažodis nebus pakeistas.
    """
    mail.send(msg)

@app.route("/prisijungti", methods=["GET", "POST"])
def prisijungti():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.PrisijungimoForma()
    if form.validate_on_submit():
        user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
        if user and bcrypt.check_password_hash(user.slaptazodis, form.slaptazodis.data):
            login_user(user, remember=form.prisiminti.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash(
                "Prisijungti nepavyko. Patikrinkite el. paštą ir slaptažodį", "danger"
            )
    return render_template("prisijungti.html", title="Prisijungti", form=form)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = forms.UzklausosAtnaujinimoForma()
    if form.validate_on_submit():
        user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
        send_reset_email(user)
        flash(
            "Jums išsiųstas el. laiškas su slaptažodžio atnaujinimo instrukcijomis.",
            "info",
        )
        return redirect(url_for("prisijungti"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = Vartotojas.verify_reset_token(token)
    if user is None:
        flash("Užklausa netinkama arba pasibaigusio galiojimo", "warning")
        return redirect(url_for("reset_request"))
    form = forms.SlaptazodzioAtnaujinimoForma()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.slaptazodis.data).decode(
            "utf-8"
        )
        user.slaptazodis = hashed_password
        db.session.commit()
        flash("Tavo slaptažodis buvo atnaujintas! Gali prisijungti", "success")
        return redirect(url_for("prisijungti"))
    return render_template("reset_token.html", title="Reset Password", form=form)


@app.route("/atsijungti")
def atsijungti():
    logout_user()
    return redirect(url_for("index"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profilio_nuotraukos", picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/paskyra", methods=["GET", "POST"])
@login_required
def account():
    form = forms.PaskyrosAtnaujinimoForma()
    if form.validate_on_submit():
        if form.nuotrauka.data:
            nuotrauka = save_picture(form.nuotrauka.data)
            current_user.nuotrauka = nuotrauka
        current_user.vardas = form.vardas.data
        current_user.el_pastas = form.el_pastas.data
        db.session.commit()
        flash("Tavo paskyra atnaujinta!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.vardas.data = current_user.vardas
        form.el_pastas.data = current_user.el_pastas
    nuotrauka = url_for(
        "static", filename="profilio_nuotraukos/" + current_user.nuotrauka
    )
    return render_template(
        "paskyra.html", title="Account", form=form, nuotrauka=nuotrauka
    )


@app.route("/irasai", methods=["POST", "GET"])
@login_required
def irasai():
    entries = False
    balance = False

    if request.method == "GET":
        action = request.args.get("action")
        if action == "Išrašas":

            page = request.args.get("page", 1, type=int)
            entries = (
                Budget.query.filter_by(vartotojas_id=current_user.id)
                .order_by(Budget.data.desc())
                .paginate(page=page, per_page=5)
            )
            test = url_for("irasai", page=page)
            print(test)
            # entries = get_entries()
        elif action == "Balansas":
            balance = get_balance()
        return render_template(
            "irasai.html", title="Įrašai", balance=balance, entries=entries
        )

    # if request.form.get("balance"):
    #         balance = get_balance()
    # elif request.form.get("entries"):
    #     page = request.args.get('page', 1, type=int)
    #     entries = Budget.query.filter_by(vartotojas_id=current_user.id).order_by(Budget.data.desc()).paginate(page=page, per_page=5)
    # entries = get_entries()
    if request.form.get("save"):
        data = dict(request.form)
        del data["save"]
        if not validate_inputs(data["income_amount"], data["expense_amount"]):
            balance = "Įvestas blogas sumos formatas, formatas turi būti: 0.00"
        else:
            add_new_entry(**data)

    return render_template(
        "irasai.html", title="Įrašai", balance=balance, entries=entries
    )





@app.errorhandler(404)
def klaida_404(klaida):
    return render_template("404.html"), 404


@app.errorhandler(403)
def klaida_403(klaida):
    return render_template("403.html"), 403


@app.errorhandler(500)
def klaida_500(klaida):
    return render_template("500.html"), 500


@app.route("/")
def index():
    return render_template("index.html")
