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
    
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])
    
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
            
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h
                if 0.8 < aspect_ratio < 1.2:
                    squares.append((x + w//2, y + h//2))  # Center of the square
    
    return squares

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def detect_pieces(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask_red1 = cv2.inRange(hsv_frame, lower_red, upper_red)
    
    lower_red = np.array([160, 100, 100])
    upper_red = np.array([180, 255, 255])
    mask_red2 = cv2.inRange(hsv_frame, lower_red, upper_red)
    
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    combined_mask = cv2.bitwise_or(mask_red, mask_blue)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pieces = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 100 < area < 10000:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                color = "Red" if cv2.pointPolygonTest(mask_red, (cX, cY), False) >= 0 else "Blue"
                pieces.append((cX, cY, color))
    
    return pieces

def detect_pieces_via_webcam():
    detected_pieces_old = {}
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open the webcam. Please check if it is connected and try again.")
        return

    black_squares_start_time = None
    calibration_points = None

    while True:
        sleep(0.1)
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        display_frame = frame.copy()

        squares = detect_black_squares(frame)
        for (x, y) in squares:
            cv2.circle(display_frame, (x, y), 5, (0, 255, 0), -1)

        if len(squares) == 4:
            if black_squares_start_time is None:
                black_squares_start_time = datetime.now()
            elif (datetime.now() - black_squares_start_time).total_seconds() >= 5:
                print("4 black squares detected for 5 seconds. Starting piece detection...")
                calibration_points = np.array(squares, dtype="float32")
                break
        else:
            black_squares_start_time = None

        cv2.imshow('Camera Frame', display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return

    while True:
        sleep(0.1)
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        if calibration_points is not None:
            frame = four_point_transform(frame, calibration_points)

        pieces = detect_pieces(frame)

        detected_pieces = {}
        for (x, y, color) in pieces:
            board_x = int((x * 14) / frame.shape[1]) + 1
            board_y = int((y * 14) / frame.shape[0]) + 1

            while (board_x, board_y) in detected_pieces:
                board_x += 1
                board_y += 1

            detected_pieces[(board_x, board_y)] = color

            cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)
            cv2.putText(frame, f"{color} ({board_x}, {board_y})", (x - 40, y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow('Detected Pieces', frame)

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