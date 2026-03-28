from flask import Flask
from flask import render_template,g,redirect,request,jsonify
from templates.utils.controller import get_db,connect_db,top_draw_graph
import sqlite3
#日付
import calendar 
from datetime import datetime

DATABASE="flaskmemo.db"

app = Flask(__name__)

@app.route("/")
def top():
    #現在の年月
    now = datetime.now()
    year=now.year
    # month=now.month
    month = request.args.get("month", default=now.month, type=int)

    # 月の補正
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    expense_list = get_db().execute("select id,date,goods,amount from expense ORDER BY date").fetchall()
    income_list = get_db().execute("select id,date,amount from income ORDER BY date").fetchall()

    total_expense = 0
    total_income = 0
    for expense_data in expense_list:
        total_expense += int(expense_data['amount'])
    for income_data in income_list:
        total_income += int(income_data['amount'])
    remaining_amount = total_income - total_expense

    labels, values, month = top_draw_graph(now,year,month)

    return render_template('index.html',expense_list=expense_list,
                                        income_list=income_list,
                                        remaining_amount=remaining_amount,
                                        labels=labels,
                                        values=values,
                                        month=month)

@app.route("/change_month")
def change_month():
    month = request.args.get("month", type=int)
    year = datetime.now().year

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    labels, values, month = top_draw_graph(datetime.now(), year, month)

    return jsonify({
        "labels": labels,
        "values": values,
        "month": month
    })

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