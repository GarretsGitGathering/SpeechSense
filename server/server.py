import os
import datetime
import uuid
from difflib import SequenceMatcher # finding similarities between strings
from flask import Flask, request, jsonify
from main import predict_intoxication, load_model, extract_features
from firebase_options import register_or_login, place_file_into_storage, update_document, get_document, bucket
from tongue_twister import generate_tongue_twister, get_spoken_script

# Initialize the Flask Server
server = Flask(__name__)

# Load the model 
model = load_model("intoxication_model.pkl")

# helper function for processing the video and saving result to database
def process_audio_and_update_document(user_id, script, temp_path, filename):
    try:
        # get the current timestamp
        curr_timestamp = datetime.datetime.now().timestamp()
        
        # load the audio file and ensure the user spoke
        spoken_text = get_spoken_script(temp_path)
        
        # find similarity percentage, ensure at least 50%
        sim_percent = SequenceMatcher(None, script, spoken_text).ratio()
        if sim_percent < .5:
            data = {"is_intoxicated": "unknown"}
            update_document("intoxication_users", user_id, f"{curr_timestamp}", data)
            return
            
        # begin finding intoxication status
        print("Predicting Intoxication")
        prediction = predict_intoxication(model, temp_path) # predict the intoxication
        
        # upload file to firebase storage and remove temp file
        with open(temp_path, "rb") as audio_file:
            place_file_into_storage("audio_recordings", f"{curr_timestamp}_{filename}", audio_file) # place the file into firebase Storage
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # data to store in firestore
        data = {
            "is_intoxicated": True if prediction[0] == 1 else False,
            "audio_recording": f"audio_recordings/{curr_timestamp}_{filename}",
            "script": script
        }
        update_document("intoxication_users", user_id, f"{curr_timestamp}", data)
        
    except Exception as error:
        print(error)

@server.route("/get_prediction", methods=["POST"])
def get_prediction():
    try: 
        # receive the user_id
        user_id = request.form.get("user_id")
        if not user_id:
            return jsonify({"error": "No user_id supplied."}), 400
        
        # receive the script
        script = request.form.get("script")
        if not script:
            return jsonify({"error": "No script supplied."}), 400
        
        # check to ensure the user sent over a file
        if "file" not in request.files:
            return jsonify({"error": "No file supplied"}), 400
        
        file = request.files["file"]    # grab the audio file
        temp_path = f"temp_{file.filename}"
        file.save(temp_path)            # save the file locally
        
        process_audio_and_update_document(user_id, script, temp_path, file.filename)    # start the video processing
        return jsonify({"status": "Audio process started"})
    except Exception as error:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": f"Error: {error}"})
    
# Route for the user to sign in
@server.route("/sign_in", methods=['POST'])
def sign_in():
    try:
        # get the users email and password
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "Email not supplied"}), 400
        
        password = request.json.get("password")
        if not password:
            return jsonify({"error": "Password not supplied"}), 400
        
        # call the register_or_login function to try logging in
        response = register_or_login(email, password)
        return response
    except Exception as error:
        return jsonify({"error": f"Error: {error}"}), 400

# Route for the user to register
@server.route("/register", methods=['POST'])
def register():
    try:
        # get the users email and password
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "Email not supplied"}), 400
        
        password = request.json.get("password")
        if not password:
            return jsonify({"error": "Password not supplied"}), 400
        
        # call the register_or_login function to try registering
        response = register_or_login(email, password, isRegistering=True)
        return response
    except Exception as error:
        return jsonify({"error": f"Error: {error}"}), 400
    
# Route to return a generated script to the user
@server.route("/get_script", methods=['POST'])
def get_script():
    try:
        # get the user_id
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "Error: No user_id supplied."}), 400
        
        # generate the script and return
        script = generate_tongue_twister()
        return jsonify({"script": script})
    except Exception as error:
        return jsonify({"error": f"Error: {error}"})
    
# Route to get the user's generation data
@server.route("/get_history", methods=['POST'])
def get_history():
    try:
        # get the user_id
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "Error: No user_id supplied."}), 400
        
        # get the user document
        user_doc = get_document("intoxication_users", user_id)
        if not user_doc:
            return jsonify({"error": "No history found for this user."}), 400
        
        return jsonify({"data": user_doc})
    except Exception as error:
        return jsonify({"error": f"Error: {error}"})
    
# Route to download the audio recordings from Firebase Storage database
@server.route("/download_audio", methods=['POST'])
def download_audio():
    try:
        # get the user_id
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "Error: No user_id supplied."}), 400
        
        # get the filepath
        audio_path = request.json.get("file_path")
        if not audio_path:
            return jsonify({"error": "Error: No audio path supplied."}), 400
        
        # generate the blob path and create the signed url
        blob = bucket.blob(audio_path)
        if not blob.exists():
            return jsonify({"error": "Error: Audio file does not exist."}), 400
        
        expiration_date = datetime.timedelta(days=1)
        audio_url = blob.generate_signed_url(expiration=expiration_date)
        
        return jsonify({"url": audio_url})
    except Exception as error:
        return jsonify({"error": f"Error: {error}"})

# route to handle pairing from a user_id to a device_id
@server.route("/pair_device", methods=['POST'])
def pair_device():
    try:
        # get the user_id 
        user_id = request.json.get("user_id", None)
        if not user_id:
            return jsonify({"error": "Missing user_id."}), 400
        
        # get the device_id they are trying to connect to
        device_id = request.json.get("device_id", None)
        if not device_id:
            return jsonify({"error": "Missing device_id."}), 400
        
        # get the device from firebase
        device_doc = get_document("intoxication_devices", device_id)
        if not device_doc:
            return jsonify({"error": "Device does not exist."}), 400
        
        # check to ensure the device doesn't currently have a key
        key = request.json.get("key", None)
        if key and key != "":
            return jsonify({"error": "Device already paired."}), 400
        
        # generate a user key 
        user_key = str(uuid.uuid4())
        
        # update the user's firebase doc with their new device_id and key
        is_set = update_document("intoxication_users", user_id, "key", user_key)
        if not is_set:
            return jsonify({"error": "Unable to update user document."}), 400
        
        return jsonify({"key": user_key})
    except Exception as error:
        return jsonify({"error": "Unable to pair to device."}), 500

if __name__ == "__main__":
    #server.run(host="0.0.0.0", port=5000)
    
    
    process_audio_and_update_document("test_user_123", "I love to drink koolaid", "segment_010_S.mp3", "segment_010_S.mp3")