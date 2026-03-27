from flask import Flask
from flask import render_template,g,redirect,request
import sqlite3
#日付
import calendar 
from datetime import datetime

DATABASE="flaskmemo.db"

app = Flask(__name__)

@app.route("/")
def top():
    expense_list = get_db().execute("select id,date,goods,amount from expense ORDER BY date").fetchall()
    income_list = get_db().execute("select id,date,amount from income ORDER BY date").fetchall()

    total_expense = 0
    total_income = 0
    for expense_data in expense_list:
        total_expense += int(expense_data['amount'])
    for income_data in income_list:
        total_income += int(income_data['amount'])
    remaining_amount = total_income - total_expense

    values = []

    now = datetime.now()
    year=now.year
    month=now.month

    month_last_day = calendar.monthrange(year,month)[1]

    labels = []
    values = []

    income_rows = get_db().execute("""
        SELECT
            strftime('%d', date) AS day,
            SUM(amount),
            SUM(SUM(amount)) OVER (ORDER BY strftime('%d', date))
        FROM income
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        GROUP BY day
        ORDER BY day
        """).fetchall()
    
    expense_rows = get_db().execute("""
        SELECT
            strftime('%d', date) AS day,
            SUM(amount),
            SUM(SUM(amount)) OVER (ORDER BY strftime('%d', date))
        FROM expense
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        GROUP BY day
        ORDER BY day
        """).fetchall()
    
    income_dict = {int(row[0]): row[1] for row in income_rows}
    expense_dict = {int(row[0]): row[1] for row in expense_rows}

    income = 0
    expense = 0
    for day in range(1, month_last_day+1):
        labels.append(f"{day}日")
        income += income_dict.get(day, 0)
        expense += expense_dict.get(day,0)
        values.append(income - expense)

    return render_template('index.html',expense_list=expense_list,
                                        income_list=income_list,
                                        remaining_amount=remaining_amount,
                                        labels=labels,
                                        values=values,
                                        month=month)




@app.route("/expense/regist",methods=['GET','POST'])
def expense_regist():
    if request.method =='POST':
        #画面からの登録情報の取得
        date = request.form.get('date')
        goods = request.form.get('goods')
        amount = request.form.get('amount')
        db = get_db()
        db.execute("insert into expense (date,goods,amount) values(?,?,?)",[date,goods,amount])
        db.commit()
        return redirect('/')
    
    return render_template('expense/regist.html')

@app.route("/income/regist",methods=['GET','POST'])
def income_regist():
    if request.method =='POST':
        #画面からの登録情報の取得
        date = request.form.get('date')
        amount = request.form.get('amount')
        db = get_db()
        db.execute("insert into income (date,amount) values(?,?)",[date,amount])
        db.commit()
        return redirect('/')
    
    return render_template('income/regist.html')

@app.route("/expense/<id>/edit",methods=['GET','POST'])
def expense_edit(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        date = request.form.get('date')
        goods = request.form.get('goods')
        amount = request.form.get('amount')
        db = get_db()
        db.execute("update expense set date=?,goods=?,amount=? where id=?",[date,goods,amount,id])
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,date,goods,amount from expense where id=?",(id,)
    ).fetchone()
    return render_template('expense/edit.html',post=post)

@app.route("/income/<id>/edit",methods=['GET','POST'])
def income_edit(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        date = request.form.get('date')
        amount = request.form.get('amount')
        db = get_db()
        db.execute("update income set date=?,amount=? where id=?",[date,amount,id])
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,date,amount from income where id=?",(id,)
    ).fetchone()
    return render_template('income/edit.html',post=post)

@app.route("/expense/<id>/delete",methods=['GET','POST'])
def expense_delete(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        db = get_db()
        db.execute("delete from expense where id=?",(id,))
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,date,goods,amount from expense where id=?",(id,)
    ).fetchone()
    return render_template('expense/delete.html',post=post)

@app.route("/income/<id>/delete",methods=['GET','POST'])
def income_delete(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        db = get_db()
        db.execute("delete from income where id=?",(id,))
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,date,amount from income where id=?",(id,)
    ).fetchone()
    return render_template('income/delete.html',post=post)

if __name__ == "__main__":
    app.run()

#database
def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db