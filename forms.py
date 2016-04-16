from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField#, FileField
from flask_wtf.file import FileField, FileAllowed, FileRequired

#from wtforms.validators import DataRequired
from wtforms import validators
from wtforms.fields.html5 import EmailField

class LoginForm(Form):
	"""Login form to access writing and settings pages"""

	username = StringField('Username', [validators.DataRequired()])
	password = PasswordField('Password', [validators.DataRequired()])
	isDeveloper = BooleanField("I'm Developer !")
	rememberMe = BooleanField("Remember Me")
	
	
class SignupForm(Form):
	username = StringField('Username', [validators.DataRequired()])
	#password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
	#confirm = PasswordField('Confirm Password', validators=[DataRequired()])
	password = PasswordField('Password', [validators.DataRequired()])
	#email = StringField('eMail', validators=[DataRequired()])
	email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
	isDeveloper = BooleanField("I'm Developer !")
	rememberMe = BooleanField("Remember Me")
	
	
class UploadAppForm(Form):

	appname = StringField('Appname', [validators.DataRequired()])
	description = StringField('Description')
	#app_zip =  FileField('App Zip'validators=[FileRequired(), FileAllowed(['zip'], 'zip only!')])
	app_zip =  FileField('App Zip', validators=[FileAllowed(['zip'], 'zip only!')])
	
	
class ConfigureIoTDeviceForm(Form):

	IoT_device_name = StringField('ioT Device name', [validators.DataRequired()])
	macAddress = StringField('ioT Device MAC address', [validators.DataRequired()])
	isActivated = BooleanField("Activate Device")
	
	
	
	
	
	
	
	
	