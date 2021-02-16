from flask import Flask,request, render_template, redirect, url_for, session,flash

app = Flask(__name__ , template_folder='Views')

@app.route('/' , methods=['GET'])
def Home():
    if request.method == 'GET':
        return render_template()
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)