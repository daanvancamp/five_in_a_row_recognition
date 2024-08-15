import cv2
import numpy as np
import json
from datetime import datetime
from time import sleep

MIN_PIECE_AREA = 100

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
        if 100 < area < 20000:
            epsilon = 0.1 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if 3 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h
                if 0.5 < aspect_ratio < 2.0:
                    squares.append((x, y, w, h))
    
    return squares

def calculate_board_coordinates(frame, black_squares):
    if len(black_squares) != 4:
        return None

    # Sort squares by x and y coordinates
    sorted_squares = sorted(black_squares, key=lambda square: (square[0], square[1]))

    # Calculate the board's bounding box
    top_left = sorted_squares[0]
    bottom_right = sorted_squares[-1]
    board_x = top_left[0]
    board_y = top_left[1]
    board_width = bottom_right[0] + bottom_right[2] - board_x
    board_height = bottom_right[1] + bottom_right[3] - board_y

    return board_x, board_y, board_width, board_height

def detect_pieces(frame, board_coords):
    if board_coords is None:
        return {}

    board_x, board_y, board_width, board_height = board_coords
    cell_width = board_width / 14
    cell_height = board_height / 14

    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])

    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv_frame, lower_red, upper_red)
    mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    combined_mask = cv2.bitwise_or(mask_red, mask_blue)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_pieces = {}
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MIN_PIECE_AREA:
            # Controleer of de contour cirkelvormig is
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity > 0.8:  # Drempelwaarde voor circulariteit
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))

                # Calculate board coordinates
                board_x = round((x - board_coords[0]) / cell_width)
                board_y = round((y - board_coords[1]) / cell_height)

                if 0 <= board_x <= 14 and 0 <= board_y <= 14:
                    piece_color = np.mean(hsv_frame[int(y-radius):int(y+radius), int(x-radius):int(x+radius)], axis=(0, 1))
                    color = "Blue" if 100 < piece_color[0] < 130 else "Red"

                    detected_pieces[(board_x, board_y)] = color

    return detected_pieces

def draw_detected_pieces(frame, detected_pieces, board_coords):
    if board_coords is None:
        return frame
    
    board_x, board_y, board_width, board_height = board_coords
    cell_width = board_width / 14
    cell_height = board_height / 14
    
    for (x, y), color in detected_pieces.items():
        piece_x = int(board_x + x * cell_width)
        piece_y = int(board_y + y * cell_height)
        
        if color == "Red":
            circle_color = (0, 0, 255)  # Rood in BGR
            text_color = (255, 255, 255)  # Wit voor betere leesbaarheid
        else:  # Blue
            circle_color = (255, 0, 0)  # Blauw in BGR
            text_color = (255, 255, 255)  # Wit voor betere leesbaarheid
        
        # Teken cirkel
        cv2.circle(frame, (piece_x, piece_y), int(min(cell_width, cell_height) / 2), circle_color, 2)
        
        # Voeg tekst toe
        cv2.putText(frame, color, (piece_x - 20, piece_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
    
    return frame

def detect_pieces_via_webcam():
    detected_pieces_old = {}
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open the webcam. Please check if it is connected and try again.")
        return

    black_squares_start_time = None
    board_coords = None

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
                board_coords = calculate_board_coordinates(frame, squares)
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
        display_frame = frame.copy()

        detected_pieces = detect_pieces(frame, board_coords)
        display_frame = draw_detected_pieces(display_frame, detected_pieces, board_coords)

        cv2.imshow('Detected Pieces', display_frame)

        detected_pieces_list = [{"color": color, "coordinates": [x, y]} for (x, y), color in detected_pieces.items()]
        data = {
            "timestamp": datetime.now().isoformat(),
            "pieces": detected_pieces_list
        }
        try:
            with open('detected_pieces.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except PermissionError:
            print("please close the detected_pieces.json file and try again")
            

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
