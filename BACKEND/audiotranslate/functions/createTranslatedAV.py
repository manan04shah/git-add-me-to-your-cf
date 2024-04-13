import createTTSFiles as ttscreate
from moviepy.editor import *
import os
#Import functions directory
import sys
sys.path.append('BACKEND')

#Helper function to convert returned list into a list of audios supported by main function
def convertToAudioList(tts_audio_files):
    audio_list = []
    for tts_audio in tts_audio_files:
        current_file = {}
        current_file["file"] = tts_audio["audio_file"]
        current_file["start_time"] = tts_audio["start_time"]
        audio_list.append(current_file)
    return audio_list

def add_duration_to_audio_list(audio_list):
    for audio_item in audio_list:
        audio_path = audio_item['file']
        audio_duration = AudioFileClip(audio_path).duration
        audio_item['duration'] = audio_duration
        audio_item['end_time'] = audio_item['start_time'] + audio_duration
    return audio_list

def split_video_with_audio_clips(video_path, audio_clips_data):
    # Load the video
    video = VideoFileClip(video_path)
    total_duration = video.duration

    clips = []
    videoclips = []

    for audio_clip_data in audio_clips_data:
        start_time = audio_clip_data['start_time']
        duration = audio_clip_data['duration']
        end_time = audio_clip_data['end_time']

        # Create a new video clip for the current audio clip
        clip = video.subclip(start_time, end_time)
        clips.append(clip)
    
    for i in range(len(clips)):
        clips[i].write_videofile(f"../videofiles/output{i}.mp4")
        videoclips.append(f"../videofiles/output{i}.mp4")

    video.close()

    return videoclips

def add_dummy_audio_fillers(audio_clips_data, dummy_audio_path):
    # Sort the audio clips data by start time
    audio_clips_data.sort(key=lambda x: x['start_time'])

    # Create a new list to store the modified audio clips data
    modified_audio_clips_data = []

    # Iterate through the sorted audio clips data
    for i in range(len(audio_clips_data)):
        # Add the current audio clip to the modified list
        modified_audio_clips_data.append(audio_clips_data[i])

        # Check if there is a gap between the current clip and the next clip
        if i < len(audio_clips_data) - 1:
            current_end_time = audio_clips_data[i]['end_time']
            next_start_time = audio_clips_data[i + 1]['start_time']

            if next_start_time > current_end_time:
                # Add a dummy audio filler
                dummy_start_time = current_end_time
                dummy_duration = next_start_time - current_end_time
                dummy_end_time = next_start_time

                dummy_audio_clip = {
                    'file': dummy_audio_path,
                    'start_time': dummy_start_time,
                    'duration': dummy_duration,
                    'end_time': dummy_end_time
                }

                modified_audio_clips_data.append(dummy_audio_clip)

    return modified_audio_clips_data

def combine_subclips(audio_files, video_files):
    combined_clips = []
    for i, audio_file in enumerate(audio_files):
        if(audio_file["file"] != "../audiofiles/dummy_audio.wav"):
            audio = AudioFileClip(audio_file["file"])
            video = VideoFileClip(video_files[i])
            video = video.set_audio(audio)
            combined_clips.append(video)
        else:
            #Remove the audio of the video and append
            video = VideoFileClip(video_files[i])
            video = video.set_audio(None)
            combined_clips.append(video)
    
    #Write each clip to a new video file
    for i, clip in enumerate(combined_clips):
        clip.write_videofile(f"../combinedfiles/output{i}.mp4")

    return combined_clips

def make_final_compilation(combined_clips):
    final_clip = concatenate_videoclips(combined_clips)
    final_clip.write_videofile("../finaloutput/final-output.mp4")
    return final_clip

def createTranslatedAV(videopath, source_lang, target_langs):
    print(os.getcwd())

    #Delete everything in combinedfiles, videofiles, audiofiles
    for file in os.listdir("../combinedfiles"):
        os.remove(f"../combinedfiles/{file}")
    for file in os.listdir("../videofiles"):
        os.remove(f"../videofiles/{file}")
    for file in os.listdir("../audiofiles"):
        os.remove(f"../audiofiles/{file}")
    

    # Extracting the audio from the video
    destination_path = "../audiofiles/extracted_audio.wav"
    video = VideoFileClip(videopath)
    audio = video.audio
    audio.write_audiofile(destination_path)
    audio.close()
    video.close()
    print("Audio extracted successfully.")

    # Getting the translations with time
    tts_audio_files = ttscreate.get_tts_with_time(destination_path, source_lang, target_langs)
    print("Translations created successfully.")

    # Converting the list of translations into a list of audio files
    audio_list = convertToAudioList(tts_audio_files)
    audio_list = add_duration_to_audio_list(audio_list)
    print("Converted to audio list successfully.")
    # print(audio_list)

    #Add filler audios
    dummy_audio_path = "../audiofiles/dummy_audio.wav"
    dummy_audio_list = add_dummy_audio_fillers(audio_list, dummy_audio_path)
    print("Dummy audio added successfully.")
    print(dummy_audio_list)

    # Removing the audio from the given video
    video = VideoFileClip(videopath)
    total_duration = video.duration
    print("Audio removed successfully.")

    #Split video file
    split_videos = split_video_with_audio_clips(videopath, dummy_audio_list)
    print("Video split successfully.")
    # print(split_videos)

    #Combine audio and video files
    combined_clips = combine_subclips(dummy_audio_list, split_videos)
    print("Combined clips successfully.")
    # print(combined_clips)

    #Make final compilation
    final_clip = make_final_compilation(combined_clips)
    print("Final compilation successful.")

    print("Your translated video is ready in final_output.mp4.")
    
    final_path = "../audiotranslate/finaloutput/final-output.mp4"
    return final_path


# createTranslatedAV(os.path.abspath("../videos/heavy.mp4"), "en", ["hi"])

if __name__ == "__main__":
    createTranslatedAV(sys.argv[1], sys.argv[2], [sys.argv[3]])
