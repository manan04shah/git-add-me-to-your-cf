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
    result = translator.translate_text(text, source_lang=source, target_lang=target)
    if type(text) is list:
        return [r.text for r in result]
    else:
        return str(result.text)


def translate_video(input_path,source_lang , target_lang, mode):

    mode = int(mode)
    if mode == 0:
        scale_factor = 1 # 60 fps -> 60 fps , retain all frames
    elif mode == 1:
        scale_factor = 0.1 # 60 fps -> 6 fps , retain 1 frame every 10 frames
    elif mode == 2:
        scale_factor = 0.05  # 60 fps -> 3 fps , retain 1 frame every 20 frames
    elif mode == 3:
        scale_factor = 0.01 # 60 fps -> 1 fps , retain 1 frame every 60 frames
    else:
        print("Error: Invalid mode")
        exit()
    
    start_time = 0
    skip_frames = int(1 / scale_factor)
    video_path = os.path.abspath(input_path)
    cap = cv2.VideoCapture(video_path)
    out_path = os.path.abspath('output.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the input video FPS
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    reader = easyocr.Reader(['en','fr','es','de'], gpu=True)

    if not cap.isOpened():
        print("Error: Couldn't open the video file")
        exit()

    font_path = "Arial.ttf"
    frame_count = 0
    previous_frame = None
    previous_translated_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % skip_frames != 0:
            if previous_translated_frame is not None:
                out.write(previous_translated_frame)
            else:
                if previous_frame is not None:
                    out.write(previous_frame)
            previous_frame = frame.copy()
            continue
        result = reader.readtext(frame)
        print(result)
        translated_frame = frame.copy()
        for detection in result:
            top_left = tuple(map(int, detection[0][0]))
            bottom_right = tuple(map(int, detection[0][2]))
            bg_color = np.mean(frame[top_left[1]-1:top_left[1]+1, bottom_right[0]:bottom_right[0]+1], axis=(0, 1))
            bg_color = tuple(map(int, bg_color))
            cv2.rectangle(translated_frame, top_left, bottom_right, bg_color, -1)
            pil_image = Image.fromarray(translated_frame)
            text_height = bottom_right[1] - top_left[1]
            font_size = int(text_height / 2)
            draw = ImageDraw.Draw(pil_image)
            text = detection[1]
            text1 = translate(str(text),source_lang,target_lang)
            font = ImageFont.truetype(font_path, font_size)
            draw.text((top_left[0], top_left[1]), text1, font=font, fill=(255-bg_color[0], 255-bg_color[1], 255-bg_color[2]))
            translated_frame = np.array(pil_image)
        out.write(translated_frame)
        previous_translated_frame = translated_frame.copy()
        previous_frame = frame.copy()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

translate_video('french2.mp4', 'FR', 'EN-GB', 2)
