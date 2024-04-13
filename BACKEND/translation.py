from googletrans import Translator

def translate_text(text):
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='hi')
    return translated_text.text

english_text = "Hello, how are you?"
hindi_text = translate_text(english_text)
print("English:", english_text)
print("Hindi:", hindi_text)