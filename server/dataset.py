import os
from moviepy import VideoFileClip   # class is necessary to open and modify video files
import pandas as pd

def split_video_to_mp3_files(input_file, output_size, output_folder, D_or_S):
    # ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    try:
        # load the video file
        video = VideoFileClip(input_file)
        duration = video.duration   # get the total duration of the video

        current_time = 0    # acts as the current time in video while looping through
        clip_number = 27     # keep track of the number of clips

        segment_data = []

        while current_time < duration:
            # find end time, and use duration if greater than created end_time
            end_time = min(current_time + output_size, duration) 

            # initialize the output file
            audio_output_file = os.path.join(output_folder, f"segment_{clip_number:03d}_{D_or_S}.mp3")

            # create the video clip
            clip = video.subclipped(current_time, end_time)
            
            # extract the audio and save as MP3
            clip.audio.write_audiofile(audio_output_file)
            print(f"Audio segment saved: {audio_output_file}")

            # add the mp3 name and classification to the dataframe
            segment_data.append({
                "name": f"segment_{clip_number:03d}_{D_or_S}.mp3",
                "Label": D_or_S
            }) 

            # increment current time and clip num
            current_time += output_size
            clip_number += 1

        # save the Dataframe as a CSV
        df = pd.DataFrame(segment_data)
        df.to_csv(f"{output_folder}/record2.csv", encoding='utf-8')
        print("CSV file created and all files kept.")

        print("All video segments have been created.")
    except Exception as error:
        print(f"Error: {error}")    
    finally:
        video.close()

def create_record_csv():
    segment_data = []
    
    for filename in os.listdir("data"):
        split_name = filename.split("_")  
        label = split_name[2]
        label = label.split(".")[0]
        
        segment_data.append({
            "name": filename,
            "Label": label
        })
    
    pd.DataFrame(segment_data).to_csv("data/record.csv", index=False)    # save the csv file to the data folder

if __name__ == "__main__": 
    # video_clip = "sober2.mp4" 
    # output_folder = "data"

    # # slit video into 60 second audio clips for drunk history
    # split_video_to_mp3_files(video_clip, 60, output_folder, "S")

    create_record_csv()