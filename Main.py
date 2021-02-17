from flask import Flask,request, render_template, redirect, url_for, session,flash
import connection as conn
app = Flask(__name__ , template_folder='Views')
app.secret_key = b'HieuPham-518H0501'
@app.route('/' , methods=['GET'])
def Home():
    if request.method == 'GET' and 'id' in session:
        query = 'SELECT * FROM subjects WHERE SubjectID IN (SELECT SubjectID FROM members WHERE AccountID = %s)'
        val = (session['id'])
        data = conn.executeQueryValData(query , val)
        return render_template('Home/Index.html' , data=data)
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
                session['id'] = data[0][0]
                return redirect(url_for('Home'))
            else:
                flash('Invalid username or password please try again')
                return redirect(url_for('Login'))
        else: return "Something went wrong"
    return "Unsupported method"

@app.route('/Quiz/<id>')
def Quiz(id):
    query = 'SELECT * FROM members WHERE SubjectID = %s AND AccountID = %s'
    val = (id , session['id'])
    data = conn.executeQueryValData(query , val)
    if len(data) > 0:
        query = 'SELECT * FROM questions WHERE SubjectID = %s'
        val = (id)
        data = conn.executeQueryValData(query , val)
        return render_template('Home/Quiz.html' , data=data)
    return redirect(url_for('Home'))

if __name__ == "__main__":
    app.run(debug=True)