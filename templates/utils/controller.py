from flask import render_template,g
import sqlite3
#日付
import calendar 
from datetime import datetime

DATABASE="flaskmemo.db"

def top_draw_graph(now,year,month):

    month_last_day = calendar.monthrange(year,month)[1]

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
    labels = []
    values = []
    for day in range(1, month_last_day+1):
        labels.append(f"{day}日")
        income += income_dict.get(day, 0)
        expense += expense_dict.get(day,0)
        values.append(income - expense)

    return labels,values,month

#database
def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db