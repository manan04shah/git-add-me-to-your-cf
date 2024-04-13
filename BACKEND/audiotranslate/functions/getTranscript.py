import wave, math, contextlib
import speech_recognition as sr

from moviepy.editor import AudioFileClip

#Delete pre-existing files, if any
try:
    os.remove("../transcriptions/transcription.txt")
except:
    pass

transcribed_audio_file_name = "../audiofiles/transcribed_speech.wav"
zoom_video_file_name = "../videos/python.mp4"

audioclip = AudioFileClip(zoom_video_file_name)
audioclip.write_audiofile(transcribed_audio_file_name)

with contextlib.closing(wave.open(transcribed_audio_file_name,'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
total_duration = math.ceil(duration / 60)

r = sr.Recognizer()

for i in range(0, total_duration):
    with sr.AudioFile(transcribed_audio_file_name) as source:
        audio = r.record(source, offset=i*60, duration=60)
    f = open("../transcriptions/transcription.txt", "w")
    f.write(r.recognize_google(audio))
    f.write(" ")
f.close()