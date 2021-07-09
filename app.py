import os
import sqlite3
from flask import Flask, render_template, g, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, usd

app = Flask(__name__)
app.secret_key = '242c8430e6634e4693718a30e863e2ee'

#Allows Jinja to covert values to USD

app.jinja_env.filters["usd"] = usd

#Connect to DB and create a cursor, Alos use row factory to ensure SQL returns dicts
@app.before_request
def before_request():
    g.db = sqlite3.connect('subzen.db')
    g.db.row_factory = dict_factory

@app.route("/", methods=['GET', 'POST'])
@login_required
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
        
        
        print(session["user_id"])
        #insert form variables into table
        g.db.execute("INSERT INTO subs(sub_name, price, pay_period, pay_date, user_id) VALUES ( ?, ?, ?, ?, ?)", (subscription, price, period, pay_date, session["user_id"],))
        g.db.commit()

        return redirect('/')

    else:

        #Add each sub from database to list, pass into template where jinja syntax will display values
        
        users = []
        for user in g.db.execute('SELECT * FROM users WHERE id =?', (session["user_id"],)):
            users.append(user)


        subs = []
        for sub in g.db.execute('SELECT * FROM subs WHERE user_id =? ORDER BY pay_date', (session["user_id"],)):
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

        return render_template("index.html", subs=subs, daily_cost=daily_cost, weekly_cost=weekly_cost, monthly_cost=monthly_cost, yearly_cost=yearly_cost, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        #Check input's from form are entered, store in variables.
        if not request.form.get("email"):
            flash('Must enter email', category='error')
            return redirect('/register')
        else:
            email = request.form.get("email")
         
        if not request.form.get("password"):
            flash('Must enter email', category='error')
            return redirect('/register')
        else:
            password = generate_password_hash(request.form.get("password"))

        g.db.execute("INSERT INTO users (email, password) VALUES ( ?, ?)", (email, password,))
        g.db.commit()

        return redirect('/login')

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        session.clear()

        #Check input's from form are entered, store in variables.
        if not request.form.get("email"):
            return redirect('/login')
        else:
            email = request.form.get("email")
         
        if not request.form.get("password"):
            return redirect('/login')
        else:
            password = request.form.get("password")

        users = []
        for user in g.db.execute('SELECT * FROM users WHERE email = ?', (email,)):
            users.append(user) 
        
        print(users)

        if len(users) != 1 or not check_password_hash(users[0]["password"], password):
            return redirect('/login')

        session["user_id"] = users[0]["id"]

        return redirect('/')

        

    return render_template("login.html")

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect('/login')

@app.route("/delete", methods=['POST'])
def delete():
    id = request.form.get('id')
    g.db.execute("DELETE FROM subs WHERE id = ?", (id,))
    g.db.commit()

    return redirect('/')

@app.route("/edit", methods=['POST', 'GET'])
@login_required
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



