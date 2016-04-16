#from index import application

from my_init import app as application

# https://www.digitalocean.com/community/tutorials/how-to-set-up-uwsgi-and-nginx-to-serve-python-apps-on-ubuntu-14-04#definitions-and-concepts

if __name__ == "__main__":
	application.debug = True
	application.run()
