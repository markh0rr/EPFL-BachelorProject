#!/usr/bin/python3 
import os
import sys 
import logging 
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/webApp/")
sys.path.insert(0,"/var/www/webApp/webApp")

from webApp import app as application 
application.secret_key = os.getenv("FLASK_SECRET_PASSWORD")