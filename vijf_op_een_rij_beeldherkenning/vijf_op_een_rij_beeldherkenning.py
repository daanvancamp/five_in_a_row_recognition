import cv2
import numpy as np
import json
from datetime import datetime
from time import sleep 


#Vreemd genoeg zijn er duplicaten van stukken, die worden in het volgende programma verwerkt en verwijderd

def crop_to_square(frame): #todo: knip zodat enkel het bord zichtbaar is
    height, width = frame.shape[:2]
    smallest_side = min(height, width)
    start_x = (width - smallest_side) // 2 
    start_y = (height - smallest_side) // 2
    square_frame = frame[start_y:start_y + smallest_side, start_x:start_x + smallest_side]
    return square_frame

def detect_pieces_via_webcam():
   
   # Open the webcam
    cap = cv2.VideoCapture(1)
    # cap = cv2.VideoCapture(0) for built-in webcam
    if not cap.isOpened():
        print("Could not open the webcam. Please check if it is connected and try again.")
        return #beeindigen

    while True:
        sleep(0)
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        cv2.imshow('Camera Frame', frame)
        cv2.waitKey(5)

        #ondergrens en bovengrens 
        lower_red = np.array([0, 0, 100])#todo: calibreer kleuren
        upper_red = np.array([100, 100, 255])
        lower_blue = np.array([100, 0, 0])
        upper_blue = np.array([255, 100, 100])

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(hsv_frame, lower_red, upper_red)#vind de kleuren
        mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)#vind de kleuren

        # Combine the masks
        combined_mask = cv2.bitwise_or(mask_red, mask_blue)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))#verbeter

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#vind contouren in de mask

        detected_pieces = {}
        for idx, contour in enumerate(contours, start=1):#start=1 for not starting at 0
            area = cv2.contourArea(contour)
            if area > 600:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2

                # Calculate new coordinates on a 15x15 gomoku board 
                board_x = (center_x * 15) // frame.shape[1] + 1
                board_y = (center_y * 15) // frame.shape[0] + 1

                piece_color = np.mean(frame[y:y+h, x:x+w], axis=(0, 1))
                color = "Blue" if piece_color[0] > piece_color[2] else "Red"

                # Add the piece to the detected pieces
                while (board_x, board_y) in detected_pieces:
                    board_x += 1
                    board_y += 1

                detected_pieces[(board_x, board_y)] = color

        # Convert detected pieces to a list of dicts for JSON
        
        detected_pieces_list = [{"color": color, "coordinates": [x, y]} for (x, y), color in detected_pieces.items()]
        # Save detected pieces to a JSON file
        data = {
            "timestamp": datetime.now().isoformat(),
            "pieces": detected_pieces_list
        }
        
        with open('detected_pieces.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        # Print detected pieces to the console
        print("Detected pieces and coordinates:")
        for (x, y), color in detected_pieces.items():
            print(f"Color: {color}, Coordinates: ({x}, {y})")

        sleep(0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    #never executed:...
    # Release resources
    cap.release()
    # Destroy all windows
    cv2.destroyAllWindows()
# Call the function
detect_pieces_via_webcam()

