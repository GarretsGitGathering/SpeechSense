import os
import time
import requests
import datetime
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

user_id = "temp_id"

def check_is_paired():
    try:
        device_doc = get_document("intoxication_devices", device_id)
        if not device_doc:
            print("Device does not exist in database. Contact support: contact@superlegitbusiness.com")
            return False

        user_id = device_doc.get("user_id", None)
        if not user_id:
            print(f"Device not paired to a user. Please pair to device in app with device id: {device_id}")
            return False

        user_doc = get_document("intoxication_users", user_id)
        if not user_doc:
            print("Not paired to a valid user.")
            return False
        
        return True
    except Exception as error:
        print(f"Unable to get user data: {error}")
        return False

# check database for most recent classification
def check_last_instance():
    # pull most recent instance from the database
    doc = get_document("intoxication_users", temp_id)
    if not doc:
        print("User does not exist.")
        return
    
    # ensure timestamp is from within at least 5 mins
    curr_timestamp = datetime.datetime().now()  # grab's current timestamp
    for key, value in doc:
        if (key + datetime.timedelta(minutes=5)) >= curr_timestamp:        # if one of the keys in the history is less than 5 minutes ago, then allow the car to start
            if not doc[key]['is_intoxicated']:
                return True
    return False


# event loop that allows car to start
if __name__ == "__main__": 
    ready_to_go = False
    while not ready_to_go:
        # ensure the device is paired 
        is_paired = False
        while not is_paired:
            is_paired = check_is_paired()
            time.sleep(5)

        # check last instance was within 5 minutes ago:
        ready_to_go = check_last_instance()

        # close relay or keep open depending upon ready_to_go
        if ready_to_go: 
            print("You're ready to drive!")
            GPIO.output(RELAY_PIN, GPIO.HIGH) 
        else: 
            print("You must upload audio that passes our test in order to drive!")
            GPIO.output(RELAY_PIN, GPIO.LOW)

            # delay by 10 seconds in between checks 
            time.sleep(10)
