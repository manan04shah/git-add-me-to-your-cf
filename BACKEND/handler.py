import cv2
import easyocr
import numpy as np

video_path = 'assets/hack.mp4'
start_time = 0

reader = easyocr.Reader(['en'], gpu=False)

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Couldn't open the video file")
    exit()

cap.set(cv2.CAP_PROP_POS_MSEC, start_time)

while True:
    ret, frame = cap.read()

    if not ret:
        break

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

        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = top_left[0] + \
            int((bottom_right[0]-top_left[0] - text_size[0])/2)
        text_y = top_left[1] + \
            int((bottom_right[1]-top_left[1] + text_size[1])/2)

        comp_bg_color = (255-bg_color[0], 255-bg_color[1], 255-bg_color[2])
        # print(comp_bg_color)

        cv2.putText(frame, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, comp_bg_color, 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
