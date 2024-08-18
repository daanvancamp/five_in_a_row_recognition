def detect_pieces_via_webcam(cell_centers):
    detected_pieces_old = {}
    print("connecting to webcam...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # extern webcam
    if not cap.isOpened():
        print("Could not open the webcam. Please check if it is connected and try again.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from the webcam. It is most likely a software error.")
            break

        frame = crop_to_square(frame)
        cv2.imshow('Camera Frame', frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect circles
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                   param1=50, param2=30, minRadius=10, maxRadius=100)
        
        detected_pieces = {}
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i, (x, y, r) in enumerate(circles[0, :]):
                
                pass

        # Detect ellipses
        contours, _ = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if len(contour) >= 5:  # need at least 5 points to fit ellipse
                ellipse = cv2.fitEllipse(contour)
                (x, y), (MA, ma), angle = ellipse
                
                # Check if it's sufficiently elliptical (you can adjust these thresholds)
                if MA > 15 and ma > 10 and MA / ma < 2:
                    
                    
                    color = "Red" if frame[int(y), int(x), 2] > frame[int(y), int(x), 0] else "Blue"
                    

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
        if detected_pieces_old != detected_pieces:
            print("Detected pieces and coordinates:")
            for (x, y), color in detected_pieces.items():
                print(f"Color: {color}, Coordinates: ({x}, {y})")
        detected_pieces_old = detected_pieces

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def crop_to_square(frame):
    height, width = frame.shape[:2]
    smallest_side = min(height, width)
    start_x = (width - smallest_side) // 2 
    start_y = (height - smallest_side) // 2
    square_frame = frame[start_y:start_y + smallest_side, start_x:start_x + smallest_side]
    return square_frame