import socket,os
import sys
import db
import subprocess
#get teh required param from another script
#check availability of given domain name -> done
#add appname to a db containing all appNames -> done
#make a new app db -> not required in mongo
#add that domainname to dev's console -> done
#acquire a new free port -> done
#create a docker container with that port -> done
#create a new redis entry with that name and port -> done
#TODO: security measures
	#should be in place via API call only
#TODO :Make a new logging server that logs everything
class Conf(object):
	"""docstring for ClassName"""
	appDb='appDb' #database for all app stuff
	appDir='allAppNames' #table to see all apps used in case of recovery		
	devConsoleDb='devDb'


def checkAvailability(appName):
	"""check in mongodb if a name is already taken or not
		return a bool
	"""
	res=db.search(Conf.appDb,Conf.appDir,{"appName":appName})
	
	if len(res)==0:
		return True
	
	return False


def addToAppDir(appName):
	try:
		inserted_id = db.insert_one(Conf.appDb,Conf.appDir,{"appName":appName})
		return inserted_id
	except: 
		return False
	# return True

def addToDev(devUsername,appName,inserted_id):
	try:
		return db.insert_one(Conf.devConsoleDb,devUsername,{"appName":appName,"inserted_id":inserted_id})
	except:
		return False

def getPort():
	"""returns a free port as an int"""
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 0))
	addr = s.getsockname()
	newPort = addr[1]
	s.close()
	return newPort
def execBashCommand(command):
	osstdout = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
	theInfo = osstdout.communicate()[0].strip()
	retCode = osstdout.returncode
	return (theInfo,retCode)
def createDocker(port,appName):
	command='docker run --name docker-'+appName+' -p '+str(port)+':80 -d -v ~/docker-nginx:/usr/share/nginx/html nginx'
	theInfo, retCode = execBashCommand(command)
	# osstdout = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
 #    theInfo = osstdout.communicate()[0].strip()
 #    retCode = osstdout.returncode
	if retCode !=0:
		return False
	#TODO: add entry into db for this container, for this port number etc
	return True
def addToRedis(port,appName):
	command = 'redis-cli rpush frontend:'+appName+'.localhost http://127.0.0.1:'+str(port)
	theInfo, retCode = execBashCommand(command)
	if retCode==0:
		return True
	return False

def main(appName,devUsername):
	if checkAvailability(appName) is False:
		print 'Not available'
		return False
	newPort = getPort()
	id = addToAppDir(appName)
	if id is False:
		print 'Unable to register app'
		return False
	if addToDev(devUsername,appName,id) is False:
		print 'Unable to add to dev console'
		return False
	if createDocker(newPort,appName) is False:
		print 'Unable to create docker'
		return False
	if addToRedis(newPort, appName) and  addToRedis(newPort, appName) is False:
		print 'Unable to create redis entry'
		return False


if __name__ == '__main__':
	main(sys.argv[1],'root')
	# appName = sys.argv[1]
	# newPort = getPort()
	# if ( createDocker(newPort,appName) and addToRedis(newPort,appName) and addToRedis(newPort,appName)):
	# 	print 'success'
	# else:
	# 	print 'failure'




