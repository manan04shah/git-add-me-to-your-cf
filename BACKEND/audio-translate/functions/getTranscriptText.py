import whisper
from moviepy.editor import *

#Delete pre-existing files, if any
try:
    os.remove("../transcriptions/transcription.txt")
except:
    pass

#Delete pre-existing files, if any
try:
    os.remove("../audiofiles/transcribed_speech.mp3")
except:
    pass

model = whisper.load_model("medium")
print("Model loaded")

transcribed_audio_file_name = "../audiofiles/transcribed_speech.mp3"
zoom_video_file_name = "../videos/python.mp4"

audioclip = AudioFileClip(zoom_video_file_name)
audioclip.write_audiofile(transcribed_audio_file_name)
print("Audio file extracted")

print("Transcribing audio file")
transcription = model.transcribe(transcribed_audio_file_name)
print(transcription['text'])

#Save the transcription as txt
with open("../transcriptions/transcription.txt", "w") as f:
    f.write(transcription['text'])