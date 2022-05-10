from budget.models import Budget

def get_entries():
    all_entries = Budget.query.all()
    print(type(all_entries))
    print(type(all_entries[0]))
    return all_entries