import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from BACKEND import handler
from moviepy.editor import *
import dropbox


#Import functions directory
import sys
sys.path.append('BACKEND')

DROPBOX_API_KEY = "sl.BzU1JJ1VcttI7jjlWeqQaURN41XmddmWwDTxzKHeCLhGpsXQ3g6c1XsQTKaT-2fx853Tk0DL5PHgAsWDJ25Omaa0mQY-LaIXWsXrNTCWrpUGX3ScklltZ4a5lp57faEaQUS8S0a941n4Fs0bPN57ZgM"

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/saveupload/") #Just saves the uploaded file locally to videos folder
async def create_upload_file(file: UploadFile = File(...)):
    upload_dir = "BACKEND/audiotranslate/videos"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    return {"filename": file.filename, "file_location": file_location}

#Function that runs a cmd command
@app.post("/runcommand/")
async def run_command(command: str):
    print(os.system(f"cd BACKEND/audiotranslate/functions && {command}"))
    return {"message": "Command executed successfully."}

#Function that uploads a file, saves it locally, then runs an OS command to run my createAV function
@app.post("/translateaudio/") #Translating ONLY the audio
async def translate_audio(videofile: UploadFile = File(...), source_lang: str = "en", target_lang: str = "hi"):
    upload_dir = "BACKEND/audiotranslate/videos"
    source_lang = source_lang.lower()
    target_lang = target_lang.lower()
    if(source_lang == "en-gb"):
        source_lang = "en"
    if(target_lang == "en-gb"):
        target_lang = "en"

    file_location = os.path.join(upload_dir, videofile.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await videofile.read())

    #Arguments
    # print(videofile.filename)
    filename = os.path.join("/home/a7x/Projects/git-add-me-to-your-cf-backend/git-add-me-to-your-cf/BACKEND/audiotranslate/videos/", videofile.filename)
    # print(filename)
    filepath = os.path.abspath(filename)
    # print(filepath)

    output_filepath = os.path.abspath("/home/a7x/Projects/git-add-me-to-your-cf-backend/git-add-me-to-your-cf/BACKEND/audiotranslate/finaloutput/final-output.mp4")

    #Run the createAV function
    print(os.system(f"cd BACKEND/audiotranslate/functions && python3 createTranslatedAV.py {filepath} {source_lang} {target_lang}"))

    dbx = dropbox.Dropbox(DROPBOX_API_KEY)
    print(dbx.users_get_current_account())

    with open(output_filepath, "rb") as f:
        dbx.files_upload(f.read(), "/audio_output.mp4", mode=dropbox.files.WriteMode.overwrite)

    #Obtain a shareable link of this uploaded file
    shared_link = dbx.sharing_create_shared_link("/audio_output.mp4")

    print(shared_link)

    return ({"shareableLink": shared_link.url})

@app.post("/translatevideo/") #Translating ONLY the video
async def translate_video(source_lang: str, target_lang: str, mode: int, videofile: UploadFile = File(...)):
    upload_dir = "BACKEND/"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_location = os.path.join(upload_dir, videofile.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await videofile.read())


    handler.translate_video(file_location, source_lang, target_lang, mode, True)

    output_filepath = "output.mp4"

    dbx = dropbox.Dropbox(DROPBOX_API_KEY)
    print(dbx.users_get_current_account())

    with open("output.mp4", "rb") as f:
        dbx.files_upload(f.read(), "/output.mp4", mode=dropbox.files.WriteMode.overwrite)

    #Obtain a shareable link of this uploaded file
    shared_link = dbx.sharing_create_shared_link("/output.mp4")

    print(shared_link)

    return ({"shareableLink": shared_link.url})

    # Return the FileResponse for the translated video
    return FileResponse(output_filepath, media_type="video/mp4", filename=videofile.filename)

@app.post("/translateav/") #Translating both the audio and video
async def translate_av(source_lang: str, target_lang: str, mode: int, videofile: UploadFile = File(...)):
    upload_dir = "BACKEND/audiotranslate/videos"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_location = os.path.join(upload_dir, videofile.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await videofile.read())

    #Arguments
    # print(videofile.filename)
    filename = os.path.join("/home/a7x/Projects/git-add-me-to-your-cf-backend/git-add-me-to-your-cf/BACKEND/audiotranslate/videos/", videofile.filename)
    # print(filename)
    filepath = os.path.abspath(filename)
    # print(filepath)

    output_filepath = os.path.abspath("/home/a7x/Projects/git-add-me-to-your-cf-backend/git-add-me-to-your-cf/BACKEND/audiotranslate/finaloutput/final-output.mp4")

    source_lang_small = source_lang.lower()
    target_lang_small = target_lang.lower()
    if(source_lang_small == "en-gb"):
        source_lang_small = "en"
    if(target_lang_small == "en-gb"):
        target_lang_small = "en"

    #Run the createAV function
    print(os.system(f"cd BACKEND/audiotranslate/functions && python3 createTranslatedAV.py {filepath} {source_lang_small} {target_lang_small}"))
    
    # Open the final output file
    translated_audio = AudioFileClip(output_filepath)

    print("BEGINNING VIDEO TRANSLATION NOW")

    source_lang_caps = source_lang.upper()
    target_lang_caps = target_lang.upper()

    handler.translate_video(filepath, source_lang_caps, target_lang_caps, mode, True)

    output_filepath = "output.mp4"

    # Open the final output file
    translated_video = VideoFileClip(output_filepath)

    # Combine the audio and video
    final_clip = translated_video.set_audio(translated_audio)

    final_clip.write_videofile("final_output.mp4")

    dbx = dropbox.Dropbox(DROPBOX_API_KEY)
    print(dbx.users_get_current_account())

    with open("final_output.mp4", "rb") as f:
        dbx.files_upload(f.read(), "/final_output.mp4", mode=dropbox.files.WriteMode.overwrite)

    #Obtain a shareable link of this uploaded file
    shared_link = dbx.sharing_create_shared_link("/final_output.mp4")

    print(shared_link)

    return ({"shareableLink": shared_link.url})