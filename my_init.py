from flask import Flask
from flask.ext.login import LoginManager


app = Flask(__name__)
app.debug = True
app.config.from_object('config')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

#from app import views
import views
