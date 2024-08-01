# import required libraries
import cv2

number_of_corners=(7,7)
# read input image
img = cv2.imread(r'./testopstellingen/bord8.jpg')

# convert the input image to a grayscale
try:
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
except:
    raise Exception("check the image path")

# Find the chess board corners
ret, corners = cv2.findChessboardCorners(gray, number_of_corners,None)

# if chessboard corners are detected
if ret == True:
   
   # Draw and display the corners

   img = cv2.drawChessboardCorners(img, number_of_corners, corners,ret)
   cv2.imshow('Chessboard',img)
   cv2.waitKey(0)
else:
    print("No chessboard detected")
cv2.destroyAllWindows()
