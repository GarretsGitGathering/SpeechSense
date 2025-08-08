import os
import numpy as np
import pickle
import librosa
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.svm import SVC    # SVC - C-Support Vector Classification
from sklearn.model_selection import train_test_split    # import train test split functionality
from sklearn.metrics import accuracy_score, confusion_matrix  # import the accuracy score to understand how well the training is going

# STANDARDIZATION OF INPUT: turning data into a standard format that can be understood by an AI model

# helper function to create a confusion matrix to visually display the models accurac
def show_confusion_matrix(y_test, y_pred):
    # Compute the confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Display the confusion matrix using a heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["bad", "good"], yticklabels=["bad", "good"])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()

def extract_features(audio_path):   # extract the features from an audio recording
    try:
        y, sampling_rate = librosa.load(audio_path)    # load the audio path
        mfcc = librosa.feature.mfcc(y=y, sr=sampling_rate, n_mfcc=13)   # mfcc = Mel-frequency cepstral coefficients (MFCCs)
        mfcc_scaled = np.mean(mfcc.T, axis=0)   # scale values to make differences between peaks more pronounced (easier to see)
        return mfcc_scaled
    except Exception as error:
        print(f"Error processing: {error}")
        return None 
    
# Load the data and extract the features (prepare the dataset for training the model!)
def load_data(audio_files, labels): # audio_files: audio recordings, labels: intoxicated or sober
    features = []   # array to hold the extracted features
    valid_labels = [] 
    
    # loop through all audio files and extract features
    for index, audio_file in enumerate(audio_files):
        audio_file_features = extract_features(audio_file)

        if audio_file_features is not None:     # ensure the audio file features are valid
            features.append(audio_file_features)
            valid_labels.append(labels[index])

    return np.array(features), np.array(valid_labels)   # return arrays so they may be used

# model training
def train_model(features, labels):
    # create the train test split
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # create model
    model = SVC(kernel="linear")
    model.fit(X_train, y_train) # fit the data with the 80% input and results data

    # Evaluating the accuracy of the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)   # find the accuracy score by comparing the y_test to the y_pred
    show_confusion_matrix(y_test, y_pred) # display the confusion matrix
    print(f"Model accuracy: {accuracy:.2f}")

    return model

# function to save the model locally
def save_model(model, filename="intoxication_model.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(model, file)
    print(f"Model saved to {filename}")

# function to load the model from storage
def load_model(filename="intoxication_model.pkl"):
    with open(filename, "rb") as file:
        model = pickle.load(file)
    return model

# function to predict if the audio recording indicates the user is intoxicated
def predict_intoxication(model, audio_path):
    features = extract_features(audio_path) # extract audio features
    if features is not None:
        prediction = model.predict([features])
        #print(f"Prediction: {prediction}")
        return prediction[0]    # return the classification
    else:
        return None   

# initialze main for this file
if __name__ == "__main__":  # checks to see if you are executing this file specifically
    # organize training data
    record_csv = "data/record.csv"
    record_df = pd.read_csv(record_csv)  # initialize the record_df with the record_csv data
    
    # grab the data from the dataframe
    audio_files = "data/"+record_df["name"]     # grab the 'name' column as an array
    labels = record_df["Label"]         # grab the labels (D or S)
    num_labels = []
    for label in labels:
        if label == "D":    
            num_labels.append(1)        # convert D or S labels to 1 or 0
        else:
            num_labels.append(0)

    features, labels = load_data(audio_files, labels)   # load dataset

    model = train_model(features, labels)   # create and train the model
    save_model(model)                       # save model locally

    # model = load_model("intoxication_model.pkl")

    # test_audio_path = "data/segment_004_S.mp3"#"data/segment_085_D.mp3"
    # prediction = predict_intoxication(model, test_audio_path)

    # if prediction == "D":
    #     print("Intoxicated, go drink water!")
    # else:
    #     print("Sober, you're good to drive!")