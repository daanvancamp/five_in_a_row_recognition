# import required libraries
import cv2
from math import sqrt

BOARD_SIZE=7
def draw_point_and_show(image,point):
    point = (368, 365)  # Hier gebruiken we gehele getallen voor de pixelcoördinaten

    # Kleur van het punt in BGR (blauw, groen, rood)
    color = (0, 0, 255)  # Rood in BGR

    # Grootte van de cirkel (straal) en dikte van de rand
    radius = 10
    thickness = -1  # Vul de cirkel in (negatieve waarde betekent vullen)

    # Tekenen van het punt
    cv2.circle(image, point, radius, color, thickness)
    cv2.namedWindow("Corners", cv2.WINDOW_NORMAL)

    cv2.imshow("Corners", image)  

def determine_coordinates_columns(list_corners)->tuple[list,list]:

    list_average_x_values=[]
    list_average_y_values=[]
    for i in list_corners:
        list_x_values_column=[]
        list_y_values_row=[]
        for corner in i:
            list_x_values_column.append(corner[0])
            list_y_values_row.append(corner[1])
        list_average_x_values.append(sum(list_x_values_column)/len(list_x_values_column))
        list_average_y_values.append(sum(list_y_values_row)/len(list_y_values_row))

    return list_average_x_values,list_average_y_values

def print_corners(corners,image):
    global BOARD_SIZE
    #order: from top left to bottom right, row by row
    corners = corners[corners[:, 0, 0].argsort()] #sort per column
    
    tuple_kolom=()
    list_corners=[]

    for i in range(BOARD_SIZE):
        for i in range(BOARD_SIZE): #order: from top left to bottom right, row by row)
            tuple_kolom+=((corners[i][0][0],corners[i][0][1]),)
        list_corners.append(tuple_kolom)
    print(list_corners)
    list_corners:list[tuple[tuple[int,int]]]

    determine_coordinates_columns(list_corners)


    for index,i in enumerate(corners):
        print("hoek"+str(index+1)+":",i)#type=numpy.ndarray

number_of_corners=(7,7)
# read input image
img = cv2.imread(r'./testopstellingen/bord8.jpg')

# convert the input image to a grayscale
try:
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
except:
    raise Exception("check the image path")

# Find the chess board corners
ret, corners = cv2.findChessboardCorners(gray, number_of_corners,None)#optional parameters: flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE

# if chessboard corners are detected
if ret == True:
   print("Chessboard detected")
   print_corners(corners,img)
   # Draw and display the corners
   img = cv2.drawChessboardCorners(img, number_of_corners, corners,ret)
   cv2.namedWindow("Chessboard", cv2.WINDOW_NORMAL)
   cv2.imshow('Chessboard',img)
   cv2.waitKey(0)
else:
    print("No chessboard detected")
cv2.destroyAllWindows()
