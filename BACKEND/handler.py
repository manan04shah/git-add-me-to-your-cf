import cv2
import easyocr
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
import deepl

deepl_api_key = os.getenv('DEEPL_API_KEY')  
translator = deepl.Translator('16f7a326-13d2-42df-b379-3c6b56c0acd7:fx')

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
        return str(result.text)


start_time = 0
skip_frames = 200  


video_path = os.path.abspath('french.mp4')

reader = easyocr.Reader(['en','fr'], gpu=True)

cap = cv2.VideoCapture(video_path)

print(cap.isOpened())
if not cap.isOpened():
    print("Error: Couldn't open the video file")
    exit()

cap.set(cv2.CAP_PROP_POS_MSEC, start_time)
frame_count = 0  


while True:
    ret, frame = cap.read()

    if not ret:
        break

    if frame_count % skip_frames != 0:  
        frame_count += 1
        continue



    result = reader.readtext(frame)
    print(result)

    for detection in result:
        top_left = tuple(map(int, detection[0][0]))
        bottom_right = tuple(map(int, detection[0][2]))

        bg_color = (0, 0, 0)

        bg_color = np.mean(frame[top_left[1]-1:top_left[1]+1,
                           bottom_right[0]:bottom_right[0]+1], axis=(0, 1))
        # print(top_left, bottom_right)
        # print(bg_color)
        bg_color = tuple(map(int, bg_color))

        # print(bg_color)

        cv2.rectangle(frame, top_left, bottom_right, bg_color, -1)

        # placeholder for now, @manan dont forget to change before translation
        text = detection[1]
        text1 = str(translate(text, 'EN', 'FR'))

        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = top_left[0] + \
            int((bottom_right[0]-top_left[0] - text_size[0])/2)
        text_y = top_left[1] + \
            int((bottom_right[1]-top_left[1] + text_size[1])/2)

        comp_bg_color = (255-bg_color[0], 255-bg_color[1], 255-bg_color[2])
        # print(comp_bg_color)

        cv2.putText(frame, text1, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, comp_bg_color, 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1  # Increment frame counter


cap.release()
cv2.destroyAllWindows()
