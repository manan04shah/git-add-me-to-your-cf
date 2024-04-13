import translateAudio as translateAudio
from gtts import gTTS

def get_tts_with_time(PATH_TO_FILE, LANGUAGE, TRANSLATION_LANGUAGES):
    tts_audio_files = []
    to_be_tts = translateAudio.get_transcription(PATH_TO_FILE, LANGUAGE, TRANSLATION_LANGUAGES)
    for i in range(0, len(to_be_tts)):
        print(to_be_tts[i]['content'], "starting at", to_be_tts[i]['start_time'], "ending at", to_be_tts[i]['end_time'])
        tts = gTTS(text=to_be_tts[i]['content'], lang=to_be_tts[i]['language'], slow=False)
        tts.save("../audiofiles\\" + str(i) + ".wav")
        to_be_tts[i]['audio_file'] = "../audiofiles\\" + str(i) + ".wav"
        tts_audio_files.append(to_be_tts[i])
    return tts_audio_files

# print(get_tts_with_time("english.wav", "en", ["es", "fr"]))
