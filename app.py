import os
import sqlite3
from flask import Flask, render_template, g, request
from werkzeug.utils import redirect

app = Flask(__name__)

#Allows Jinja to covert values to USD
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

app.jinja_env.filters["usd"] = usd

#Connect to DB and create a cursor, Alos use row factory to ensure SQL returns dicts
@app.before_request
def before_request():
    g.db = sqlite3.connect('subzen.db')
    g.db.row_factory = dict_factory

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":

        #Check input's from form are entered, store in variables.
        if not request.form.get("subscription"):
            return redirect('/')
        else:
            subscription = request.form.get("subscription")
         
        if not request.form.get("price"):
            return redirect('/')
        else:
            price = request.form.get("price")

        if not request.form.get("period"):
            return redirect('/')
        else:
            period = request.form.get("period")

        if not request.form.get("pay_date"):
            return redirect('/')
        else:
            pay_date = request.form.get("pay_date")
        
        user = 1

        #insert form variables into table
        g.db.execute("INSERT INTO subs(sub_name, price, pay_period, pay_date, user_id) VALUES ( ?, ?, ?, ?, ?)", (subscription, price, period, pay_date, user,))
        g.db.commit()

        return redirect('/')

    else:

        #Add each sub from database to list, pass into template where jinja syntax will display values
        subs = []
        for sub in g.db.execute('SELECT * FROM subs'):
            subs.append(sub) 


        daily_cost = 0
        for sub in subs:
            if sub['pay_period'] == 'daily':
                daily_cost += sub['price'] 
            elif sub['pay_period'] == 'weekly':
                daily_cost += sub['price'] / 7
            elif sub['pay_period'] == 'monthly':
                daily_cost += sub['price'] / 30.4
            else:
                daily_cost += sub['price'] / 365         

        weekly_cost = daily_cost * 7
        monthly_cost = daily_cost * 30.4
        yearly_cost = daily_cost * 365

        return render_template("index.html", subs=subs, daily_cost=daily_cost, weekly_cost=weekly_cost, monthly_cost=monthly_cost, yearly_cost=yearly_cost)

@app.route("/delete", methods=['POST'])
def delete():
    id = request.form.get('id')
    g.db.execute("DELETE FROM subs WHERE id = ?", (id,))
    g.db.commit()

    return redirect('/')

@app.route("/edit", methods=['POST', 'GET'])
def edit():
    
    id = request.form.get('id')
    print(id)
    sub = []
    for item in g.db.execute('SELECT * FROM subs WHERE id = ?', (id,)):
        sub.append(item)
    return render_template('edit.html', sub=sub)

@app.route("/update", methods=['POST'])
def update():
    if not request.form.get("subscription"):
            return redirect('/')
    else:
        subscription = request.form.get("subscription")
        
    if not request.form.get("price"):
        return redirect('/')
    else:
        price = request.form.get("price")

    if not request.form.get("period"):
        return redirect('/')
    else:
        period = request.form.get("period")

    if not request.form.get("pay_date"):
        return redirect('/')
    else:
        pay_date = request.form.get("pay_date")
    
    id = request.form.get("id")

    print(subscription, price, period, pay_date, id)

    g.db.execute('UPDATE subs SET sub_name = ?, price = ?, pay_period = ?, pay_date = ? WHERE id = ?', (subscription, price, period, pay_date, id,))
    g.db.commit()

    return redirect('/')

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == '__main__':
    app.run()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



