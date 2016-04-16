import urllib2, urllib
import random
import time

myPort = "80"
user_id = "a"
iot_id = "12"
token = "8TKH1NWQNROPA9TE7D03ZSS203ENUA6E"

NUM_REQUESTS = 3

for i in range(NUM_REQUESTS):
	
	temp = random.uniform(30, 45)	# temperature in celcius
	humidity = random.uniform(10, 90)	# humidity in percentage
	wind_speed = random.uniform(0.5, 20.0)	# in km/hr
	
	data = {}
	data['temp'] = temp
	data['humidity'] = humidity
	data['wind_speed'] = wind_speed
	
	myParameters = { "iot_id": iot_id, "user_id": user_id, "token": token, "data": data}
	url = "http://localhost:%s/upload_iot_data/?%s" % (myPort, urllib.urlencode(myParameters)) 
	response = urllib2.urlopen(url).read()
	print "request #", i, "sent"
	time.sleep(0.5)
	

