import speechmatics
import httpcore

def get_transcription(filepath, source_lang, target_langs):
    # target_langs is a list of languages to translate to

    # Define constants
    API_KEY = "QH9Q9f0UjjhJ6vyzdJUxZyHlF3HN3BHq"
    PATH_TO_FILE = filepath
    LANGUAGE = source_lang  # Transcription language
    TRANSLATION_LANGUAGES = target_langs
    CONNECTION_URL = f"wss://eu2.rt.speechmatics.com/v2/{LANGUAGE}"

    # Create a transcription client
    ws = speechmatics.client.WebsocketClient(
        speechmatics.models.ConnectionSettings(
            url=CONNECTION_URL,
            auth_token=API_KEY,
            generate_temp_token=True,  # Enterprise customers don't need to provide this parameter
        )
    )

    # Define an event handler to print the translations & append it to the list of to be TTS-ed
    def print_translation(msg):
        msg_type = "Final" if msg['message'] == "AddPartialTranslation" else "Partial"
        language = msg['language']
        translations = [translation_segment['content'] for translation_segment in msg['results']]
        current_tts_dict = get_tts_dict(msg)
        to_be_tts.append(current_tts_dict)

    def get_tts_dict(msg):
        current_statement_dict = {}
        current_statement_dict['content'] = msg['results'][0]['content']
        current_statement_dict['start_time'] = msg['results'][0]['start_time']
        current_statement_dict['end_time'] = msg['results'][0]['end_time']
        current_statement_dict['language'] = msg['language']
        return current_statement_dict

    # Register the event handler for partial translation
    ws.add_event_handler(
        event_name=speechmatics.models.ServerMessageType.AddPartialTranslation,
        event_handler=print_translation,
    )

    # Register the event handler for full translation
    ws.add_event_handler(
        event_name=speechmatics.models.ServerMessageType.AddTranslation,
        event_handler=print_translation,
    )

    settings = speechmatics.models.AudioSettings()
    translation_config = speechmatics.models.RTTranslationConfig(
        target_languages=TRANSLATION_LANGUAGES,
    )
    transcription_config = speechmatics.models.TranscriptionConfig(
        language=LANGUAGE,
        translation_config=translation_config,
    )

    print("Starting transcription (type Ctrl-C to stop):")
    try:
        to_be_tts = []
        with open(PATH_TO_FILE, 'rb') as fd:
            ws.run_synchronously(fd, transcription_config, settings)
        sorted_to_be_tts = sorted(to_be_tts, key=lambda x: x['language'])
        return sorted_to_be_tts
    except KeyboardInterrupt:
        print("\nTranscription stopped.")
    except httpcore.exceptions.RequestError as e:
        if str(e).startswith('401'):
            print('Invalid API key - Check your API_KEY at the top of the code!')
        else:
            raise e