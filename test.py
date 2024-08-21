import cv2

# Maak VideoCapture-objecten voor dezelfde webcam
cap1 = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap2 = cv2.VideoCapture(0,cv2.CAP_DSHOW)

while True:
    # Lees frames van beide VideoCapture-objecten
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if ret1 and ret2:
        # Toon de frames
        cv2.imshow('Frame 1', frame1)
        cv2.imshow('Frame 2', frame2)

    # Druk op 'q' om de loop te beëindigen
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release de VideoCapture-objecten en sluit alle vensters
cap1.release()
cap2.release()
cv2.destroyAllWindows()

