import cv2
import numpy as np

#push c on your keyboard when you would like to calibrate the color
#push q on your keyboard when you would like to quit

def get_dominant_color(image, k=4, image_processing_size=None):
    if image_processing_size is not None:
        image = cv2.resize(image, image_processing_size, 
                           interpolation=cv2.INTER_AREA)
    pixels = np.float32(image.reshape(-1, 3))
    n_colors = k
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    dominant = palette[np.argmax(counts)]
    return dominant

def get_color_bounds(hsv_color):
    h_sensitivity = 5
    s_sensitivity = 50
    v_sensitivity = 50
    
    lower_bound = np.array([
        max(0, hsv_color[0] - h_sensitivity),
        max(0, hsv_color[1] - s_sensitivity),
        max(0, hsv_color[2] - v_sensitivity)
    ])
    
    upper_bound = np.array([
        min(180, hsv_color[0] + h_sensitivity),
        min(255, hsv_color[1] + s_sensitivity),
        min(255, hsv_color[2] + v_sensitivity)
    ])
    
    return lower_bound, upper_bound

def main():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    calibrate = False
    lower_bound = None
    upper_bound = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        if calibrate:
            # Convert frame to HSV
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Get the dominant color in the frame
            dominant_color_bgr = get_dominant_color(frame)
            dominant_color_hsv = cv2.cvtColor(np.uint8([[dominant_color_bgr]]), 
                                              cv2.COLOR_BGR2HSV)[0][0]
            
            # Get the color bounds for the dominant color
            lower_bound, upper_bound = get_color_bounds(dominant_color_hsv)
            
            # Print the color bounds
            print("Lower bound:", lower_bound)
            print("Upper bound:", upper_bound)
            
            calibrate = False

        if lower_bound is not None and upper_bound is not None:
            # Convert frame to HSV
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create a mask using the color bounds
            mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
            
            # Show the mask
            cv2.imshow("Mask", mask)

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            calibrate = True

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
