from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Put your secret key here'
DB_NAME = 'paas'

UPLOAD_FOLDER = '/datastore/'
ALLOWED_EXTENSIONS = set(['zip', 'png', 'jpg', 'jpeg', 'gif'])
SEND_FILE_MAX_AGE_DEFAULT = 1	# cache is deleted after 1 second. It is deliberately set low to show security features of files

DATABASE = MongoClient()[DB_NAME]

USERS_TABLE = "users"
USERS_APPS_TABLE = "users_apps"
APPS_TABLE = "apps"
USERS_IOT_TABLE = "users_iot"	# contains _id (mac address), IoT_device_name, user_id, isActivated (can be True/False), token (for authentication when sending IoT data)
IOT_DATA_TABLE = "iot_data"		# contains iot_id, user_id, data		


#USERS_COLLECTION = DATABASE.users
#USERS_APPS_COLLECTION = DATABASE.users_apps	# simply contains 3 cols, _id, user_id, app_id indicating app has permission on user. This user can be a customer or a developer. 
#APPS_COLLECTION = DATABASE.apps	# contains _id (ie app_id), developer_id, description, date_modified

DEBUG = True
