#from app import app, lm
from my_init import app
from my_init import lm

from flask import request, redirect, render_template, url_for, flash, g, jsonify, send_from_directory, make_response
from flask.ext.login import login_user, logout_user, login_required, current_user

from forms import LoginForm, SignupForm, UploadAppForm, ConfigureIoTDeviceForm
from user import User
#from third_party_app import App

import db_api

import datetime
import logging
import os, random, string

from werkzeug.security import generate_password_hash
from werkzeug import  secure_filename

@app.route('/')
def home():
	return render_template('home.html')

	
@app.route('/dashboard')
@login_required
def dashboard():
	if current_user.is_developer() is True:
		third_party_apps = db_api.search(app.config['DATABASE'], app.config['APPS_TABLE'], {"developer_id": current_user.get_id()}, snapshot=True)
		real_third_party_apps = []	# the cursor object is a pain in the ass while updating its objects in the for loop !
		for third_party_app in third_party_apps:
			num_downloads = db_api.count(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": third_party_app['_id']})
			third_party_app['num_downloads'] = num_downloads
			real_third_party_apps.append(third_party_app)
			#flash(third_party_app, category='info')
			
		return render_template('dashboard.html', title='Dashboard', third_party_apps=real_third_party_apps)
	else:
		third_party_apps = db_api.search(app.config['DATABASE'], app.config['APPS_TABLE'], {})
		real_third_party_apps = []
		for third_party_app in third_party_apps:
			num_downloads = db_api.count(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": third_party_app['_id']})
			permission = db_api.exists(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": third_party_app['_id'], "user_id": current_user.get_id()})
			third_party_app['num_downloads'] = num_downloads
			third_party_app['permission'] = permission
			real_third_party_apps.append(third_party_app)
			
		iot_data = db_api.search(app.config['DATABASE'], app.config['IOT_DATA_TABLE'], {"user_id": current_user.get_id()})
		iot_devices = db_api.search(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"user_id": current_user.get_id()})
		
		return render_template('dashboard.html', title='Dashboard', third_party_apps=real_third_party_apps, iot_data=iot_data, iot_devices=iot_devices)
	

@app.route('/toggle_app_permission')
@login_required
def toggle_app_permission():
	if current_user.is_developer() is False:
		app_id = request.args.get('app_id')
		isPermGranted = db_api.exists(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": app_id, "user_id": current_user.get_id()})
		if isPermGranted is True:
			db_api.delete(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": app_id, "user_id": current_user.get_id()})
			return jsonify(result="False")	# json somehow converts it into all lowercase and we are string matching it on the client side
		else:
			db_api.insert(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": app_id, "user_id": current_user.get_id()})
			return jsonify(result="True")
	
	flash("Only Customers (non developers) can toggle app permissions!", category='error')
	return render_template('home.html')
	
	
@app.route('/toggle_iot_activation')
@login_required
def toggle_iot_activation():
	if current_user.is_developer() is False:
		iot_id = request.args.get('iot_id')
		iot_device = db_api.search_one(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": iot_id, "user_id": current_user.get_id()})
		if iot_device:
			if iot_device['isActivated'] is True:
				result = db_api.update_one(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": iot_id, "user_id": current_user.get_id()}, { "$set": {"isActivated": False} } )
				return jsonify(result="False")
			else:
				token = gen_token(32);
				result = db_api.update_one(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": iot_id, "user_id": current_user.get_id()}, { "$set": {"isActivated": True, "token": token} } )	# each new acivation changes the unique token for the identification of the IoT device
				return jsonify(result="True")
		else:
			flash("You do not own the IoT deivce " + iot_id, category='error')
			return render_template('dashboard.html')
	
	flash("Only Customers (non developers) can toggle IoT device activations!", category='error')
	return render_template('home.html')
	
	
@app.route('/delete_app')
@login_required
def delete_app():
	if current_user.is_developer() is True:
		app_id = request.args.get('app_id')
		appEntry = db_api.search_one(app.config['DATABASE'], app.config['APPS_TABLE'], {"developer_id": current_user.get_id(), "_id": app_id})
		if not appEntry:
			return jsonify(result="Error: trying to delete non owned app")
			
		try:
			fileName = appEntry['app_zip']
			uploadDir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.get_id())
			deleteFile(uploadDir, fileName)
			
			result = db_api.delete(app.config['DATABASE'], app.config['APPS_TABLE'], {"_id": app_id, "developer_id": current_user.get_id()})
			result2 = db_api.delete(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"app_id": app_id})

			return jsonify(result=result)
		except Exception as e:
			flash(str(e), category='error')
			return jsonify(result=str(e))
			
	flash("Only Developers can delete apps!", category='error')
	return render_template('home.html')
	
	
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if request.method == 'POST' and form.validate_on_submit():	# validate_on_submit() is a flask.ext.wtf function that manages form submit and HTTP method: PUT/POST/GET
		#user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
		user = db_api.search_one(app.config['DATABASE'], app.config['USERS_TABLE'], {"_id": form.username.data})
		if user:
			flash("This user already exists!", category='info')
			return render_template('signup.html', title='Signup', form=form)
		
		try:
			uploadDir = os.path.join(app.config['UPLOAD_FOLDER'], form.username.data)
			os.makedirs(uploadDir)
			
			rememberMe = form.rememberMe.data
			pass_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
			#app.config['USERS_COLLECTION'].insert({"_id": form.username.data, "password": pass_hash, "email": form.email.data, "isDeveloper": form.isDeveloper.data})
			db_api.insert(app.config['DATABASE'], app.config['USERS_TABLE'], {"_id": form.username.data, "password": pass_hash, "email": form.email.data, "isDeveloper": form.isDeveloper.data})
			
			
			#user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})	# the user has just been added in the above line
			user = db_api.search_one(app.config['DATABASE'], app.config['USERS_TABLE'], {"_id": form.username.data})
			
			
			
			user_obj = User(user)
			login_user(user_obj, remember=rememberMe)
			flash("Registered and logged in successfully!", category='success')
			return redirect(request.args.get("next") or url_for("home"))
		except Exception as e:
			flash("Failed to Register and Login!", category='error')
			flash(str(e), category='error')
			
	return render_template('signup.html', title='Signup', form=form)	# we are still not registered :(
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if request.method == 'POST' and form.validate_on_submit():	# validate_on_submit() is a flask.ext.wtf function that manages form submit and HTTP method: PUT/POST/GET
		user = db_api.search_one(app.config['DATABASE'], app.config['USERS_TABLE'], {"_id": form.username.data})
		rememberMe = form.rememberMe.data
		if user and User.validate_login(user, form.password.data, form.isDeveloper.data):
			user_obj = User(user)
			login_user(user_obj, remember=rememberMe)
			flash("Logged in successfully!", category='success')
			return redirect(request.args.get("next") or url_for("home"))
		flash("Wrong username or password!", category='error')
	return render_template('login.html', title='login', form=form)	# we are still not logged in :(


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))


@app.route('/upload_app', methods=['GET', 'POST'])
@login_required
def upload_app():
	if current_user.is_developer() is True:
		form = UploadAppForm()
		if request.method == 'POST' and form.validate_on_submit():	# validate_on_submit() is a flask.ext.wtf function that manages form submit and HTTP method: PUT/POST/GET
			third_party_app = db_api.search_one(app.config['DATABASE'], app.config['APPS_TABLE'], {"_id": form.appname.data})
			
			if third_party_app:
				if third_party_app['developer_id'] != current_user.get_id():
					flash("An app with this name exists and you are not its developer!", category='error')
					return render_template('upload_app.html', title='upload app', form=form)
				else:
					flash("Updating your previous app!", category='info')
					#if form.app_zip.data:
					#fileData = request.FILES[form.app_zip.name].read()
					fileName = form.app_zip.data.filename
					fileData = form.app_zip.data
					uploadDir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.get_id())
					upload(fileName, fileData, uploadDir)
					
					db_api.update_one(app.config['DATABASE'], app.config['APPS_TABLE'], {"_id": form.appname.data}, {"_id": form.appname.data, "developer_id": current_user.get_id(), "description": form.description.data, "date_modified": str(datetime.datetime.now()), "app_zip": fileName})
					
					return redirect(request.args.get("next") or url_for("dashboard"))
			else:
				try:
					#if form.app_zip.data:
					#fileData = request.FILES[form.app_zip.name].read()
					fileName = form.app_zip.data.filename
					fileData = form.app_zip.data
					uploadDir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.get_id())
					upload(fileName, fileData, uploadDir)
					
					db_api.insert(app.config['DATABASE'], app.config['USERS_APPS_TABLE'], {"user_id": current_user.get_id(), "app_id": form.appname.data})
					db_api.insert(app.config['DATABASE'], app.config['APPS_TABLE'], {"_id": form.appname.data, "developer_id": current_user.get_id(), "description": form.description.data, "date_modified": str(datetime.datetime.now()), "app_zip": fileName})
					
					#third_party_app_obj = App(third_party_app)
					
					flash("App registered successfully!", category='success')
					return redirect(request.args.get("next") or url_for("dashboard"))
				except Exception as e:
					flash("App registration failed!", category='error')
					flash(str(e), category='error')
					return render_template('upload_app.html', title='upload app', form=form)
				
		return render_template('upload_app.html', title='upload app', form=form)
	
	flash("Only Developers can upload apps!", category='error')
	return render_template('home.html')

	
@app.route('/upload_iot_data/', methods=['GET'])
def upload_iot_data():
	#if current_user.is_developer() is False:
	#	return render_template('upload_iot_data.html')
	#flash("Only Customers (non developers) can upload IoT Data!", category='error')
	#return render_template('home.html')

	user_id = request.args.get('user_id')
	iot_id = request.args.get('iot_id')
	token = request.args.get('token')
	data = request.args.get('data')
	isAuthenticated = db_api.exists(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": iot_id, "user_id": user_id, "token": token})	# device should be activated for listening to new data
	if isAuthenticated is False:
		flash("Unauthorized: IoT data transfer to "+ iot_id + " failed", category='error')
		return make_response(render_template('error.html'), 403)
	
	isActivated = db_api.exists(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": iot_id, "user_id": user_id, "isActivated": True})
	if isActivated is False:
		flash("Inactivate device: IoT data transfer to "+ iot_id + " failed", category='error')
		return make_response(render_template('upload_iot_data.html'))
	
	db_api.insert(app.config['DATABASE'], app.config['IOT_DATA_TABLE'], {"iot_id": iot_id, "user_id": user_id, "data": data})
	flash("IoT data transfered to IoT device id "+ iot_id, category='success')
	return make_response(render_template('upload_iot_data.html'))
	
	

@app.route('/configure_iot_device', methods=['GET', 'POST'])
@login_required
def configure_iot_device():
	if current_user.is_developer() is False:
		form = ConfigureIoTDeviceForm()
		if request.method == 'POST' and form.validate_on_submit():
			IoT_device = db_api.search_one(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": form.macAddress.data})
			if IoT_device and IoT_device['isActivated'] == True:
				flash("IoT device already activated with customer " + IoT_device['user_id'], category='error')
				return render_template('configure_iot_device.html', title='configure IoT Device', form=form)
			else:
				token = gen_token(32);
				db_api.insert(app.config['DATABASE'], app.config['USERS_IOT_TABLE'], {"_id": form.macAddress.data, "user_id": current_user.get_id(), "IoT_device_name": form.IoT_device_name.data, "isActivated": form.isActivated.data, "token": token})
				flash("IoT Device registered successfully!", category='success')
				return redirect(request.args.get("next") or url_for("dashboard"))
					
		return render_template('configure_iot_device.html', title='configure IoT Device', form=form)
		
	flash("Only Customers (non developers) can upload IoT Data!", category='error')
	return render_template('home.html')
	


@lm.user_loader
def load_user(username):
	#u = app.config['USERS_COLLECTION'].find_one({"_id": username})
	u = db_api.search_one(app.config['DATABASE'], app.config['USERS_TABLE'], {"_id": username})
	if not u:
		return None
	return User(u)

	
@app.before_request
def before_request():
    g.user = current_user	
	
	
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
	
	
@login_required
def upload(fileName, fileData, uploadDir):
    # Check if the file is one of the allowed types/extensions
    if fileData and allowed_file(fileName):
        # Make the filename safe, remove unsupported chars
        fileName = secure_filename(fileName)
        # Move the file form the temporal folder to
        # the upload folder we setup
		
        fileData.save(os.path.join(uploadDir, fileName))
		
        # Redirect the user to the uploaded_file route, which
		# Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
		
        #return redirect(url_for('uploaded_file', filename=fileName))
		
		
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
	uploadDir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.get_id())
	return send_from_directory(uploadDir, filename)


@login_required
def deleteFile(uploadDir, fileName):
	os.remove(os.path.join(uploadDir, fileName))


def gen_token(N):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))









 
	