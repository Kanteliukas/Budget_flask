from budget.models import Budget
from budget import current_user, db

def add_new_entry(
    income_amount,
    expense_amount,
    sender,
    extra_information,
    payment_option,
    bought_goods_or_services,
):
    if income_amount != "":
        budget = Budget(
            "Pajamos",
            float(income_amount),
            sender=sender,
            extra_information=extra_information,
            vartotojas_id=current_user.id,
        )
    if expense_amount != "":
        budget = Budget(
            "Išlaidos",
            float(expense_amount),
            payment_option=payment_option,
            bought_goods_or_services=bought_goods_or_services,
            vartotojas_id=current_user.id,
        )
    db.session.add(budget)
    db.session.commit()