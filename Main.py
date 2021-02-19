from flask import Flask,request, render_template, redirect, url_for, session,flash
import connection as conn
from datetime import datetime
from time import time
app = Flask(__name__ , template_folder='Views')
app.secret_key = b'HieuPham-518H0501'
@app.route('/' , methods=['GET'])
def Home():
    if request.method == 'GET' and 'id' in session:
        AccountID = session['id']
        status = []
        if AccountID == 1:
            query = 'SELECT * FROM subjects'
            data = conn.executeQueryData(query)
        else:
            query = 'SELECT * FROM subjects WHERE SubjectID IN (SELECT SubjectID FROM members WHERE AccountID = %s)'
            val = (AccountID)
            data = conn.executeQueryValData(query , val)
        for item in data:
            query = 'SELECT * FROM results WHERE AccountID = %s AND SubjectID = %s'
            val = (AccountID, item[0])
            resultInfo = conn.executeQueryValData(query , val)
            if len(resultInfo) == 1 and resultInfo[0][7] != None:
                status.append(True)
            else:
                status.append(False)
        return render_template('Home/Index.html' , data=data , status=status)
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
    if request.method == 'GET' and 'id' in session:
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
    elif request.method == 'POST' and 'id' in session:
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
    return 'Unauthorized' , 401

@app.route('/Result/<id>' , methods=['GET'])
def Result(id):
    if 'id' in session:
        AccountID = session['id']
        query = 'SELECT * FROM results WHERE AccountID = %s AND SubjectID = %s'
        val = (AccountID, id)
        data = conn.executeQueryValData(query,val)
        if len(data) == 1 and data[0][7] != None:
            query = 'SELECT SubjectName FROM subjects WHERE SubjectID = %s'
            val = (id)
            subject = conn.executeQueryValData(query,val)
            return render_template('Home/Result.html' , data=data , subject=subject)
        else:
            return redirect(url_for('Home'))
    return 'Unauthorized' , 401
@app.route('/Logout')
def Logout():
    session.pop('id' , None)
    return redirect(url_for("Home"))

@app.route('/CreateExam', methods=['POST' , 'GET'])
def CreateExam():
    if request.method == 'POST' and 'id' in session and session['id'] == 1:
        data = request.form
        query = 'INSERT INTO Subjects(SubjectName,StartTime,EndTime,Time) VALUES(%s,%s,%s,%s)'
        val = (data['SubjectName'] , data['StartTime'] , data['EndTime'], data['Time'])
        conn.executeQueryValNonData(query,val)
        return redirect(url_for('Home'))
    elif request.method == 'GET' and 'id' in session and session['id'] == 1:
        return render_template('Home/CreateExam.html')
    return 'Unsupported method'

@app.route('/AddQuestion/<id>' , methods=['POST' , 'GET'])
def AddQuestion(id):
    if request.method == 'GET' and 'id' in session and session['id'] == 1:
        query = 'SELECT * FROM Subjects WHERE SubjectID = %s'
        val = (id)
        data = conn.executeQueryValData(query,val)
        if len(data) == 1:
            return render_template('Home/AddQuestion.html' , data=data)
        else:
            return redirect(url_for('Home'))
    elif request.method == 'POST' and 'id' in session and session['id'] == 1:
        data = request.form
        correct = ''
        if data['Answer'] == 'A':
            correct = data['SentenceA']
        elif data['Answer'] == 'B':
            correct = data['SentenceB']
        elif data['Answer'] == 'C':
            correct = data['SentenceC']
        elif data['Answer'] == 'D':
            correct = data['SentenceD'] 
        query = 'INSERT INTO questions(question, ansA, ansB, ansC, ansD, correctAns, SubjectID) VALUES(%s,%s,%s,%s,%s,%s,%s)'
        val = (data['Question'], data['SentenceA'], data['SentenceB'], data['SentenceC'], data['SentenceD'], correct, id)
        conn.executeQueryValNonData(query,val)
        flash('Add question successfully!')
        query = 'SELECT * FROM Subjects WHERE SubjectID = %s'
        val = (id)
        data = conn.executeQueryValData(query,val)
        if len(data) == 1:
            return render_template('Home/AddQuestion.html' , data=data)
        return 'Something went wrong!!!'
    return 'Unauthorized' , 401

@app.route('/AddStudent/<SubID>/',methods=['GET'])
@app.route('/AddStudent/<SubID>/<AccID>',methods=['GET'])
def AddStudent(SubID,AccID=None):
    if request.method == 'GET' and 'id' in session and session['id'] == 1:
        if AccID == None:
            query = 'SELECT * FROM subjects WHERE SubjectID = %s'
            val = (SubID)
            data = conn.executeQueryValData(query,val)
            if len(data) == 1:
                query = 'SELECT * FROM accounts WHERE AccountID NOT IN (SELECT AccountID FROM members WHERE SubjectID = %s)'
                val = (SubID)
                accInfo = conn.executeQueryValData(query,val)
                return render_template('Home/AddStudent.html' , data=data, accInfo=accInfo)
            else:
                return redirect(url_for('Home'))
        else:
            query = 'SELECT * FROM subjects WHERE SubjectID = %s'
            val = (SubID)
            data = conn.executeQueryValData(query,val)
            query = 'SELECT * FROM accounts WHERE AccountID = %s'
            val = (AccID)
            acc = conn.executeQueryValData(query,val)
            if len(data) == 1 and len(acc) == 1:
                query = 'SELECT * FROM members WHERE AccountID = %s AND SubjectID = %s'
                val = (AccID , SubID)
                memberInfo = conn.executeQueryValData(query, val)
                if len(memberInfo) == 1:
                    flash('Account already exists in this exam!')
                else:
                    query = 'INSERT INTO members VALUES(%s,%s)'
                    val = (AccID,SubID)
                    conn.executeQueryValNonData(query,val)
                    flash('Add Student Successfully!')
                query = 'SELECT * FROM accounts WHERE AccountID NOT IN (SELECT AccountID FROM members WHERE SubjectID = %s)'
                val = (SubID)
                accInfo = conn.executeQueryValData(query,val)
                return render_template('Home/AddStudent.html' , data=data, accInfo=accInfo)
            else:
                return redirect(url_for('Home'))
    return "Unsupported Method"

if __name__ == "__main__":
    app.run(debug=True)