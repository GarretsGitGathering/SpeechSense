import io
from mimetypes import guess_type
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from flask import jsonify
import requests

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'face-recognition-306d9.appspot.com'})

# create the firestore client to communicate with the firestore application
db = firestore.client()

# initialize storage
bucket = storage.bucket()

# function to update an existing collection with a document
def update_document(collection_name, document_name, field_name, field_value):
    try:
        # create a reference to the document
        document_reference = db.collection(collection_name).document(document_name)

        # set the data into the document
        document_reference.set({field_name: field_value}, merge=True)

        print(f"Document {document_name} has been updated.")

    except Exception as error:  # called an error catch, VERY COMMON IN PRODUCTION
        print(f"An error has occurred: {error}")


# function to pull data out of a document
def get_document(collection_name, document_name):
    try:
        # create a reference to the document
        document_reference = db.collection(collection_name).document(document_name)

        # get the document data
        doc = document_reference.get()

        if doc.exists:
            print(f"Got data from {document_name}.")
            return doc.to_dict()
        else:
            return None
    except Exception as error:
        print(f"An error has occurred: {error}")
        return None

# Function to allow the user to create an account or sign in
def register_or_login(email, password, isRegistering=False):
    status = "signInWithPassword"  # input to Google to sign in
    if isRegistering:
        status = "signUp"  # input to Google to sign up

    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:{status}?key=nononononononononno"
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=data)
        response_data = response.json()

        if response.status_code == 200:
            id_token = response_data.get("idToken")
            user_id = response_data.get("localId")  # This is the unique Firebase user ID
            return jsonify({"idToken": id_token, "user_id": user_id})

        return jsonify({"error": response_data.get("error", "An unknown error occurred.")})

    except Exception as error:
        print(f"An error has occurred: {error}")
        return jsonify({"error": str(error)})


# Function to place files into Firebase Storage
def place_file_into_storage(folder_path, filename, file):
    blob_path = f'{folder_path}/{filename}'  # Path in Firebase storage
    blob = bucket.blob(blob_path)  # Create blob reference
    
    blob.upload_from_file(file)  # Upload file
    print(f"File {filename} successfully uploaded to {blob_path}")

# Function to grab files out of Firebase Storage
def grab_file_from_storage(folder_path, file_name):
    blob_path = f'{folder_path}/{file_name}'  # Path of the file in storage
    blob = bucket.blob(blob_path)  # Get blob reference

    if blob.exists():  # Check if the blob exists in Firebase storage
        file_bytes = blob.download_as_bytes()  # Download file content as bytes
        print("Successfully downloaded file")
        return io.BytesIO(file_bytes)  # Return a BytesIO stream of the file content
    else:
        raise FileNotFoundError("File not found in Firebase storage.")
    
# Function to grab file options from a folder in Firebase Storage
def get_files_in_storage(folder_path):
    blob_path = f'{folder_path}/'
    blobs = bucket.list_blobs(prefix=blob_path)
    return [blob.name for blob in blobs]

if __name__ == "__main__":
    # collection_name = "users"
    # document_name = "test_user_123"
    # # update_document(collection_name, document_name, "clothes_1", "*reference_to_png_in_storage*")

    # # call the get_document function
    # data = get_document(collection_name, document_name)
    # print("Here is the document data:")
    # print(data)

    email = "alaricasemail@gmail.com"
    password = "superSecurePassword"
    register_or_login(email, password)
