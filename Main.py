from flask import Flask,request, render_template, redirect, url_for, session,flash
import connection as conn
from datetime import datetime
from time import time
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

@app.route('/Quiz/<id>' , methods=['POST' , 'GET'])
def Quiz(id):
    if request.method == 'GET':
        AccountID = session['id']
        query = 'SELECT * FROM members WHERE SubjectID = %s AND AccountID = %s'
        val = (id , AccountID)
        data = conn.executeQueryValData(query , val)
        if len(data) > 0:
            today = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            query = 'SELECT * FROM questions WHERE SubjectID = %s'
            val = (id)
            data = conn.executeQueryValData(query , val)
            query = 'SELECT * FROM results WHERE AccountID = %s AND SubjectID = %s'
            val = (AccountID , id)
            resultInfo = conn.executeQueryValData(query , val)
            query = 'SELECT * FROM subjects WHERE SubjectID = %s'
            val = (id)
            subjectInfo = conn.executeQueryValData(query , val)
            if len(resultInfo) == 1:
                startTime = resultInfo[0][4]
                currentTime = time() - startTime
                timeToTake = int(currentTime / 60)
                return render_template('Home/Quiz.html' , data=data , id=id, subjectInfo=subjectInfo, timeToTake=timeToTake)
            else:
                query = 'INSERT INTO results(AccountID, SubjectID , StartTime, Time) VALUES(%s , %s, %s, %s)'
                val = (AccountID , id , today, time())
                conn.executeQueryValNonData(query,val)
                return render_template('Home/Quiz.html' , data=data , id=id, subjectInfo=subjectInfo)
        return redirect(url_for('Home'))
    elif request.method == 'POST':
        data = request.form.to_dict()
        query = 'SELECT COUNT(*) FROM questions WHERE SubjectID = %s'
        val = (id)
        questInfo = conn.executeQueryValData(query , val)
        numQuestion = questInfo[0][0]
        numCorrect = 0
        for i in range(1,numQuestion+1):
            questionID = data['quest' + str(i)]
            answer = ''
            if 'question' + str(i) in data:
                answer = data['question' + str(i)]
            query = 'SELECT correctAns FROM questions WHERE questionID = %s'
            val = (questionID)
            answerInfo = conn.executeQueryValData(query, val)
            correctAns = answerInfo[0][0]
            if correctAns == answer:
                numCorrect += 1
        AccountID = session['id']
        today = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        numIncorrect = numQuestion - numCorrect
        scoreEachQuestion = 10 / numQuestion
        score = numCorrect * scoreEachQuestion
        query = 'UPDATE results SET EndTime = %s, NumCorrect = %s , NumIncorrect = %s, score = %s WHERE AccountID = %s AND SubjectID = %s'
        val = (today, numCorrect , numIncorrect, score , AccountID, id)
        conn.executeQueryValNonData(query, val)
        url = '/Result/{}'
        return redirect(url.format(id))

@app.route('/Result/<id>' , methods=['GET'])
def Result(id):
    AccountID = session['id']
    query = 'SELECT * FROM results WHERE AccountID = %s AND SubjectID = %s'
    val = (AccountID, id)
    data = conn.executeQueryValData(query,val)
    query = 'SELECT SubjectName FROM subjects WHERE SubjectID = %s'
    val = (id)
    subject = conn.executeQueryValData(query,val)
    return render_template('Home/Result.html' , data=data , subject=subject)

@app.route('/Logout')
def Logout():
    session.pop('id' , None)
    return redirect(url_for("Home"))

if __name__ == "__main__":
    app.run(debug=True)