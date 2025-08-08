import os
import time
import requests
from dotenv import load_dotenv

import RPi.GPIO as GPIO
from firebase_options import get_document, update_document

# call load_dotenv to load environ variables
load_dotenv()

device_id = os.environ.get("DEVICE_ID")
key = os.environ.get("KEY")

# relay pin
RELAY_PIN = 7

# set the GPIO mode for relay
GPIO.setmode(GPIO.BCM) # 0 for low and 1 for high (off or on)
GPIO.setup(RELAY_PIN, GPIO.OUT) # sending data to relay


# check database for most recent classification
def check_last_instance():
    # pull most recent instance from the database
    
    
    # ensure timestamp is from within at least 5 mins
    
    
    # check the classification
    
    
    # return classification