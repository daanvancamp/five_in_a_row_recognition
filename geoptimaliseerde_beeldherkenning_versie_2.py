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
        if 210 < area < 20000:
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

    # lower_red = np.array([0 ,178, 155]) #origineel: (0, 0, 100)
    # lower_red= np.array([0, 150, 150])
    # upper_red = np.array([7, 255, 255])#origineel: (100, 100, 255)
    # upper_red = np.array([10, 255, 255])

    # lower_blue = np.array([110 ,111, 183])#origineel: (100, 0, 0)
    # lower_blue = np.array([100, 150, 150])
    # upper_blue = np.array([ 118, 217 ,255])#origineel: (255, 100, 100)
    # upper_blue = np.array([ 130, 255, 255])

    lower_red= np.array([0,0,100])
    upper_red = np.array([100,100,255])

    lower_blue = np.array([100,0,0])
    upper_blue = np.array([255,100,100])

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv_frame, lower_red, upper_red)
    mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    combined_mask = cv2.bitwise_or(mask_red, mask_blue)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_pieces = {}
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1:
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2

            # Calculate board coordinates
            board_x = round((center_x - board_x) / cell_width)
            board_y = round((center_y - board_y) / cell_height)

            if 0 <= board_x <= 14 and 0 <= board_y <= 14:
                piece_color = np.mean(frame[y:y+h, x:x+w], axis=(0, 1))
                color = "Blue" if piece_color[0] > piece_color[2] else "Red"

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
            rect_color = (0, 0, 255)  # Rood in BGR
            text_color = (255, 255, 255)  # Wit voor betere leesbaarheid
        else:  # Blue
            rect_color = (255, 0, 0)  # Blauw in BGR
            text_color = (255, 255, 255)  # Wit voor betere leesbaarheid
        
        # Teken rechthoek
        cv2.rectangle(frame, (piece_x, piece_y), (piece_x + int(cell_width), piece_y + int(cell_height)), rect_color, 2)
        
        # Voeg tekst toe
        cv2.putText(frame, color, (piece_x, piece_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
    
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
        cv2.imshow('Camera Frame', frame)

        cv2.waitKey(5)

        detected_pieces = detect_pieces(frame, board_coords)
        display_frame = draw_detected_pieces(display_frame, detected_pieces, board_coords)

        cv2.imshow('pieces', display_frame)


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