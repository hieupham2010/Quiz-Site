from flask import Flask,request, render_template, redirect, url_for, session,flash
import connection as conn
app = Flask(__name__ , template_folder='Views')
app.secret_key = b'HieuPham-518H0501'
@app.route('/' , methods=['GET'])
def Home():
    if request.method == 'GET' and 'username' in session:
        return render_template('Home/Index.html')
    return redirect(url_for('Login'))

@app.route('/Login', methods=['POST' , 'GET'])
def Login():
    if request.method == 'GET':
        return render_template('Account/Login.html')
    elif request.method == 'POST':
        query = 'SELECT * FROM accounts WHERE Username = %s AND Password = %s'
        form = request.form
        val = (form['username'] , form['password'])
        data = conn.executeQueryValData(query , val)
        if data != False:
            if len(data) == 1:
                session['username'] = form['username']
                return redirect(url_for('Home'))
            else:
                flash('Invalid username or password please try again')
                return redirect(url_for('Login'))
        else: return "Something went wrong"
    return "Unsupported method"


if __name__ == "__main__":
    app.run(debug=True)