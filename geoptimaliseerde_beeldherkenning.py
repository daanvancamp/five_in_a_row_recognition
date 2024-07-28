import cv2
import numpy as np
import json
from datetime import datetime
from time import sleep

def crop_to_square(frame):
    height, width = frame.shape[:2]
    smallest_side = min(height, width)
    start_x = (width - smallest_side) // 2 
    start_y = (height - smallest_side) // 2
    square_frame = frame[start_y:start_y + smallest_side, start_x:start_x + smallest_side]
    return square_frame

def detect_black_squares(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_black = np.array([103, 50, 50])
    upper_black = np.array([123, 255, 255])
    
    mask = cv2.inRange(hsv, lower_black, upper_black)
    
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    squares = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 800 < area < 20000:
            epsilon = 0.1 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if 3 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h
                if 0.5 < aspect_ratio < 2.0:
                    squares.append((x, y, w, h))
    
    return squares

def detect_pieces_via_webcam():
    detected_pieces_old = {}
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open the webcam. Please check if it is connected and try again.")
        return

    black_squares_start_time = None

    while True:
        sleep(0)
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        display_frame = frame.copy()

        squares = detect_black_squares(frame)
        for (x, y, w, h) in squares:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if len(squares) == 4:
            if black_squares_start_time is None:
                black_squares_start_time = datetime.now()
            elif (datetime.now() - black_squares_start_time).total_seconds() >= 5:
                print("4 black squares detected for 5 seconds. Starting piece detection...")
                break
        else:
            black_squares_start_time = None

        cv2.imshow('Camera Frame', display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return

    while True:
        sleep(0)
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        cv2.imshow('Camera Frame', frame)
        cv2.waitKey(5)

        lower_red = np.array([0, 0, 100])
        upper_red = np.array([100, 100, 255])
        lower_blue = np.array([100, 0, 0])
        upper_blue = np.array([255, 100, 100])

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(hsv_frame, lower_red, upper_red)
        mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

        combined_mask = cv2.bitwise_or(mask_red, mask_blue)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_pieces = {}
        for idx, contour in enumerate(contours, start=1):
            area = cv2.contourArea(contour)
            if 10000 > area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2

                board_x = (center_x * 15) // frame.shape[1] + 1
                board_y = (center_y * 15) // frame.shape[0] + 1

                piece_color = np.mean(frame[y:y+h, x:x+w], axis=(0, 1))
                color = "Blue" if piece_color[0] > piece_color[2] else "Red"

                while (board_x, board_y) in detected_pieces:
                    board_x += 1
                    board_y += 1

                detected_pieces[(board_x, board_y)] = color

        detected_pieces_list = [{"color": color, "coordinates": [x, y]} for (x, y), color in detected_pieces.items()]
        data = {
            "timestamp": datetime.now().isoformat(),
            "pieces": detected_pieces_list
        }
        
        with open('detected_pieces.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        if detected_pieces_old != detected_pieces:
            print("Detected pieces and coordinates:")
            for (x, y), color in detected_pieces.items():
                print(f"Color: {color}, Coordinates: ({x}, {y})")
        detected_pieces_old = detected_pieces

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):  # RECALIBRATE
            cap.release()
            cv2.destroyAllWindows()
            detect_pieces_via_webcam()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_pieces_via_webcam()