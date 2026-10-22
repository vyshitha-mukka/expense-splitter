from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "change-me"

# Simple in-memory storage (resets when the container restarts)
expenses = []


def parse_people(text):
    return [p.strip().title() for p in text.split(",") if p.strip()]


def compute_balances():
    bal = {}
    for e in expenses:
        share = e["amount"] / len(e["people"])
        bal[e["payer"]] = bal.get(e["payer"], 0) + e["amount"]
        for p in e["people"]:
            bal[p] = bal.get(p, 0) - share
    return {k: round(v, 2) for k, v in bal.items()}


def compute_settlements(bal):
    creditors = sorted([[n, a] for n, a in bal.items() if a > 0.005], key=lambda x: -x[1])
    debtors = sorted([[n, -a] for n, a in bal.items() if a < -0.005], key=lambda x: -x[1])
    result, i, j = [], 0, 0
    while i < len(debtors) and j < len(creditors):
        pay = min(debtors[i][1], creditors[j][1])
        result.append({"from": debtors[i][0], "to": creditors[j][0], "amount": round(pay, 2)})
        debtors[i][1] -= pay
        creditors[j][1] -= pay
        if debtors[i][1] < 0.005:
            i += 1
        if creditors[j][1] < 0.005:
            j += 1
    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add():
    try:
        amount = float(request.form["amount"])
        payer = request.form["payer"].strip().title()
        people = parse_people(request.form["people"])
        desc = request.form["description"].strip()
        if amount <= 0 or not payer or not people or not desc:
            raise ValueError
    except (ValueError, KeyError):
        flash("Please fill all fields correctly.")
        return redirect(url_for("index"))
    expenses.append({"description": desc, "amount": amount, "payer": payer, "people": people})
    flash("Expense added!")
    return redirect(url_for("expenses_page"))


@app.route("/expenses")
def expenses_page():
    return render_template("expenses.html", expenses=expenses)


@app.route("/settle")
def settle():
    bal = compute_balances()
    return render_template("settle.html", balances=bal, settlements=compute_settlements(bal))


@app.route("/clear", methods=["POST"])
def clear():
    expenses.clear()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
