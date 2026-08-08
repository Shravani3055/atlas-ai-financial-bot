def check_budget_alert(spent, budget):
    if budget == 0:
        return None

    percent = (spent / budget) * 100

    if percent >= 90:
        return "🚨 You are about to exhaust your budget!"
    elif percent >= 80:
        return "⚠️ You crossed 80% of your budget!"
    return None