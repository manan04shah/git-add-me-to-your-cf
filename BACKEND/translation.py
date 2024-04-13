import deepl
import os

deepl_api_key = os.getenv('DEEPL_API_KEY')  
translator = deepl.Translator(deepl_api_key)

def translate(text, source, target):
    sources = ["BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI", "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH"]
    targets = ["BG", "CS", "DA", "DE", "EL", "EN-GB", "EN-US", "ES", "ET", "FI", "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT-BR", "PT-PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH"]

    if source not in sources:
        return False
    if target not in targets:
        return False
    
    #unsupported languages return false
    
    result = translator.translate_text(text, source_lang=source, target_lang=target)
    if type(text) is list:
        return [r.text for r in result]
    else:
        return result.text
