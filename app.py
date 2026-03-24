from flask import Flask
from flask import render_template,g,redirect,request
import sqlite3
DATABASE="flaskmemo.db"

app = Flask(__name__)

@app.route("/")
def top():
    memo_list = get_db().execute("select id,date,goods,amount from memo").fetchall()
    return render_template('index.html',memo_list=memo_list)

@app.route("/regist",methods=['GET','POST'])
def regist():
    if request.method =='POST':
        #画面からの登録情報の取得
        date = request.form.get('date')
        goods = request.form.get('goods')
        amount = request.form.get('amount')
        db = get_db()
        db.execute("insert into memo (date,goods,amount) values(?,?,?)",[date,goods,amount])
        db.commit()
        return redirect('/')
    
    return render_template('regist.html')

@app.route("/<id>/edit",methods=['GET','POST'])
def edit(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        date = request.form.get('date')
        goods = request.form.get('goods')
        amount = request.form.get('amount')
        db = get_db()
        db.execute("update memo set date=?,goods=?,amount=? where id=?",[date,goods,amount,id])
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,date,goods,amount from memo where id=?",(id,)
    ).fetchone()
    return render_template('edit.html',post=post)

@app.route("/<id>/delete",methods=['GET','POST'])
def delete(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        db = get_db()
        db.execute("delete from memo where id=?",(id,))
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,date,goods,amount from memo where id=?",(id,)
    ).fetchone()
    return render_template('delete.html',post=post)


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