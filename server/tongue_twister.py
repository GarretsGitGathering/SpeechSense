import random
import speech_recognition
import pydub

# Define word lists with alliteration
word_groups = {
    "S": ["slippery", "silly", "sizzling", "sneaky", "shiny", "sassy"],
    "P": ["Peter", "plump", "playful", "picky", "purple", "puzzled"],
    "T": ["tiny", "tricky", "tumbling", "twisting", "terrific", "tense"],
    "B": ["bouncing", "big", "blazing", "bubbly", "bold", "brilliant"],
    "C": ["cranky", "curious", "clumsy", "cautious", "colorful", "cheerful"],
    "F": ["fancy", "furry", "fidgety", "fearless", "fast", "flimsy"]
}

sentence_templates = [
    "{adj1} {noun1} {verb1} {adv1} over {adj2} {noun2}.",
    "{noun1} {verb1} a {adj1} {noun2} while {adv1} {verb2}.",
    "How can a {adj1} {noun1} {verb1} {adv1} when the {adj2} {noun2} {verb2}?"
]

verbs = ["twisted", "tripped", "tumbled", "bounced", "plopped", "flipped"]
adverbs = ["quickly", "clumsily", "slowly", "gracefully", "awkwardly", "boldly"]

def generate_tongue_twister():
    letter = random.choice(list(word_groups.keys()))  # Choose a random starting letter
    adj1, adj2 = random.sample(word_groups[letter], 2)
    noun1, noun2 = random.sample(word_groups[letter], 2)
    verb1, verb2 = random.sample(verbs, 2)
    adv1 = random.choice(adverbs)

    sentence = random.choice(sentence_templates).format(
        adj1=adj1, adj2=adj2, noun1=noun1, noun2=noun2, verb1=verb1, verb2=verb2, adv1=adv1
    )

    return sentence

# function to get the spoken script from an audio file
def get_spoken_script(audio_path):
    # check if mp3, convert to wav if so
    if (audio_path.split(".")[-1] == "mp3"):
        audio_path = convert_mp3_to_wav(audio_path)
    
    # initialize the recognizer
    recognizer = speech_recognition.Recognizer()    
    
    # load the audio file and extract the text
    with speech_recognition.AudioFile(audio_path) as source:
        # load audio into memory
        audio_data = recognizer.record(source)
        
        # recognize audio with Google (because it's free)
        text = recognizer.recognize_google(audio_data)
        
    return text

# helper function to convert an mp3 to a wav
def convert_mp3_to_wav(audio_path):
    # create the destination path
    split_path = audio_path.split("/")
    audio_file = split_path[len(split_path) - 1]
    audio_filename = audio_file.split(".")[0]
    dest_path = audio_filename + ".wav"
    
    # extract the sound from the mp3 and export the .wav
    sound = pydub.AudioSegment.from_mp3(audio_path)
    sound.export(dest_path, format="wav")
    
    return dest_path

# Example Usage
if __name__ == "__main__":
    print(get_spoken_script("data/segment_015_D.mp3"))