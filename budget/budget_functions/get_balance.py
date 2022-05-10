from budget.models import Budget

def get_balance():
    all_entries = Budget.query.all()
    amounts = []
    for entry in all_entries:
        amounts.append(entry.amount)
    return sum(amounts)