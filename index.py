from flask import Flask, render_template
application = Flask(__name__)
application.debug = True

@application.route("/appRegister")
def showAppRegister():
	return render_template('appRegister.html')
	
@application.route("/")
def index():
	return render_template('index.html')
    # return "<h1 style='color:blue'>Hello There!</h1>"

@application.route('/hello/<name>')
def hello(userName=None):
	return render_template('hello.html', name=userName)	
	
	
if __name__ == "__main__":
    application.run(host='0.0.0.0')
