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

def show_camera_feed(cap):
    print("Showing camera feed. Press 'c' to start calibration or 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            return False
        
        frame = crop_to_square(frame)
        cv2.imshow('Camera Feed', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            return True
        elif key == ord('q'):
            return False

def calibrate(cap):
    print("Calibration started. Please follow the instructions.")
    
    calibration_steps = [
        ("background", "Place the gray blanket in view."),
        ("board", "Place the white board on the gray blanket."),
        ("pieces", "Place a blue piece and a red piece on the board.")
    ]
    
    calibration_images = {}
    
    for step, instruction in calibration_steps:
        print(f"\n{instruction}")
        print("Press 'c' when ready, or 'q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                return None
            
            frame = crop_to_square(frame)
            cv2.imshow('Calibration', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                calibration_images[step] = frame.copy()
                break
            elif key == ord('q'):
                return None
    
    print("\nCalibration complete. Waiting 5 seconds for stability...")
    sleep(5)
    
    return calibration_images

def detect_pieces(frame, calibration_images):
    background = calibration_images['background']
    board = calibration_images['board']
    pieces = calibration_images['pieces']

    # Convert all images to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv_background = cv2.cvtColor(background, cv2.COLOR_BGR2HSV)
    hsv_board = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
    hsv_pieces = cv2.cvtColor(pieces, cv2.COLOR_BGR2HSV)
    
    # Create masks for board and pieces
    lower_board = np.array(hsv_background.mean(axis=(0,1)) - 30, dtype=np.uint8)
    upper_board = np.array(hsv_board.mean(axis=(0,1)) + 30, dtype=np.uint8)
    lower_pieces = np.array(hsv_board.mean(axis=(0,1)) - 30, dtype=np.uint8)
    upper_pieces = np.array(hsv_pieces.max(axis=(0,1)) + 30, dtype=np.uint8)

    board_mask = cv2.inRange(hsv_frame, lower_board, upper_board)
    pieces_mask = cv2.inRange(hsv_frame, lower_pieces, upper_pieces)
    
    # Find contours of the board and pieces
    board_contours, _ = cv2.findContours(board_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pieces_contours, _ = cv2.findContours(pieces_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not board_contours:
        return {}, frame
    
    # Find the largest contour (assumed to be the board)
    board_contour = max(board_contours, key=cv2.contourArea)
    
    # Get board dimensions
    board_x, board_y, board_w, board_h = cv2.boundingRect(board_contour)
    
    detected_pieces = {}
    for contour in pieces_contours:
        area = cv2.contourArea(contour)
        if 100 < area < 10000:  # Adjust these values based on your piece size
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Calculate board coordinates
            board_x = int((center_x - board_x) / board_w * 15) + 1
            board_y = int((center_y - board_y) / board_h * 15) + 1
            
            # Determine color
            piece_color = np.mean(frame[y:y+h, x:x+w], axis=(0, 1))
            color = "Blue" if piece_color[0] > piece_color[2] else "Red"
            
            detected_pieces[(board_x, board_y)] = color
    
    return detected_pieces, frame

def detect_pieces_via_webcam():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open the webcam. Please check if it is connected and try again.")
        return

    if not show_camera_feed(cap):
        print("Camera preview cancelled. Exiting.")
        cap.release()
        cv2.destroyAllWindows()
        return

    calibration_images = calibrate(cap)
    if calibration_images is None:
        print("Calibration failed or was cancelled. Exiting.")
        cap.release()
        cv2.destroyAllWindows()
        return

    detected_pieces_old = {}

    print("\nPiece detection started. Press 'q' to quit or 'c' to recalibrate.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        detected_pieces, display_frame = detect_pieces(frame, calibration_images)

        # Draw detected pieces on the display frame
        for (x, y), color in detected_pieces.items():
            cv2.circle(display_frame, (int(x * frame.shape[1] / 15), int(y * frame.shape[0] / 15)), 10, (0, 255, 0), -1)

        cv2.imshow('Game Board', display_frame)

        detected_pieces_list = [{"color": color, "coordinates": [x, y]} for (x, y), color in detected_pieces.items()]
        data = {
            "timestamp": datetime.now().isoformat(),
            "pieces": detected_pieces_list
        }
        
        with open('detected_pieces.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        if detected_pieces_old != detected_pieces:
            print("\nDetected pieces and coordinates:")
            for (x, y), color in detected_pieces.items():
                print(f"Color: {color}, Coordinates: ({x}, {y})")
        detected_pieces_old = detected_pieces

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting the program.")
            break
        elif key == ord('c'):
            print("\nRecalibrating...")
            if show_camera_feed(cap):
                calibration_images = calibrate(cap)
                if calibration_images is None:
                    print("Recalibration failed or was cancelled. Continuing with previous calibration.")
                else:
                    print("Recalibration successful.")
            else:
                print("Recalibration cancelled. Continuing with previous calibration.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_pieces_via_webcam()