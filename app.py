from flask import Flask, render_template, request, redirect, url_for
from db_config import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        data = (
            request.form['accno'],
            request.form['name'].upper(),
            request.form['mobile'],
            request.form['email'].upper(),
            request.form['address'].upper(),
            request.form['city'].upper(),
            request.form['country'].upper(),
            float(request.form['balance'])
        )
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bank VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data)
        conn.commit()
        conn.close()
        return render_template("message.html", message="Account added successfully!")
    return render_template('add_account.html')

@app.route('/accounts')
def view_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bank")
    accounts = cursor.fetchall()
    conn.close()
    return render_template('view_accounts.html', accounts=accounts)

@app.route('/search', methods=['GET', 'POST'])
def search_account():
    if request.method == 'POST':
        accno = request.form['accno']
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bank WHERE ACCNO=%s", (accno,))
        account = cursor.fetchone()
        conn.close()
        return render_template('search_account.html', account=account)
    return render_template('search_account.html')

@app.route('/update/<accno>', methods=['GET', 'POST'])
def update_account(accno):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = (
            request.form['name'].upper(),
            request.form['mobile'],
            request.form['email'].upper(),
            request.form['address'].upper(),
            request.form['city'].upper(),
            request.form['country'].upper(),
            float(request.form['balance']),
            accno
        )
        cursor.execute("""
            UPDATE bank SET 
            NAME=%s, MOBILE=%s, EMAIL=%s, ADDRESS=%s,
            CITY=%s, COUNTRY=%s, BALANCE=%s WHERE ACCNO=%s
        """, data)
        conn.commit()
        conn.close()
        return render_template("message.html", message="Account updated successfully!")
    else:
        cursor.execute("SELECT * FROM bank WHERE ACCNO=%s", (accno,))
        account = cursor.fetchone()
        conn.close()
        return render_template("update_account.html", account=account)

@app.route('/delete/<accno>')
def delete_account(accno):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bank WHERE ACCNO=%s", (accno,))
    conn.commit()
    conn.close()
    return render_template("message.html", message="Account deleted successfully!")

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        accno = request.form['accno']
        ttype = request.form['type']
        amount = float(request.form['amount'])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BALANCE FROM bank WHERE ACCNO=%s", (accno,))
        result = cursor.fetchone()
        if not result:
            return render_template("message.html", message="Account not found!")
        balance = result[0]

        if ttype == 'debit':
            if balance - amount < 5000:
                return render_template("message.html", message="Insufficient balance (min Rs.5000 required)")
            balance -= amount
        else:
            balance += amount

        cursor.execute("UPDATE bank SET BALANCE=%s WHERE ACCNO=%s", (balance, accno))
        conn.commit()
        conn.close()
        return render_template("message.html", message="Transaction successful!")
    return render_template("transaction.html")

if __name__ == '__main__':
    app.run(debug=True)
