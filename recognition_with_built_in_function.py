# import required libraries
from operator import index
import cv2
from math import sqrt
import numpy as np

BOARD_SIZE=8
corners_to_be_found=BOARD_SIZE-1

def draw_point_and_show(image,point):
    color = (0, 0, 255)  # Rood in BGR

    radius = 10
    thickness = -1  

    cv2.circle(image, point, radius, color, thickness)
    cv2.namedWindow("Corners", cv2.WINDOW_NORMAL)

    cv2.imshow("Corners", image)  

def determine_average_distances(list_corners_tuples,corners)->tuple[int,int]:
    for column in list_corners_tuples:
        list_x_values_column=[]
        list_y_values_column=[]
        for corner in column:
            list_x_values_column.append(corner[0])#=x value
            list_y_values_column.append(corner[1])#=y value
    average_horizontal_distance_column=(max(list_x_values_column)-min(list_x_values_column))/(corners_to_be_found)
    average_vertical_distance_column=(max(list_y_values_column)-min(list_y_values_column))/(corners_to_be_found)

    
    corners= corners[corners[0, :, 0].argsort()]
    print(corners)

    tuple_rij=()

    list_tuples_corners=[]
    for i in range(corners_to_be_found):
        for x in range(corners_to_be_found): #order: from top left to bottom right, row by row)
            tuple_rij+=((corners[i][0][0],corners[i][0][1]),)
        list_tuples_corners.append(tuple_rij)

    for row in list_tuples_corners:
        list_x_values_row=[]
        list_y_values_row=[]
        for corner in row:
            list_x_values_row.append(corner[0])#=x value
            list_y_values_row.append(corner[1])#=y value
    
    average_horizontal_distance_row=(max(list_x_values_row)-min(list_x_values_row))/(corners_to_be_found)
    average_vertical_distance_row=(max(list_y_values_row)-min(list_y_values_row))/(corners_to_be_found)


    return (average_horizontal_distance_column,average_vertical_distance_column),(average_horizontal_distance_row,average_vertical_distance_row)

def append_element(corners,element):
    element=[[element]] #same layout
    print(element)
    if element is not None and element:
        corners=np.append(corners,element,axis=0)
        print(corners)
    return corners


def extrapolate_other_corners(list_corners_tuples,corners,average_horizontal_distance,average_vertical_distance)->list:
    list_corners_tuples:list[list[tuple[int,int]]]
    #print(list_corners_tuples)
    print(corners)
    for index_column,column in enumerate(list_corners_tuples):
            for index_row,corner in enumerate(column) :
                #add the cells to the right and left
                if index_column==0:
                    # corners.np.append((corner[0]-average_horizontal_distance,corner[1]))
                    corners=append_element(corners,(corner[0]-average_horizontal_distance,corner[1]))
                elif index_column==BOARD_SIZE-1:
                    corners=append_element(corners,(corner[0]+average_horizontal_distance,corner[1]))
                
                #add the cells under and above
                if index_row==0:
                    corners=append_element(corners,(corner[0],corner[1]-average_vertical_distance)) #corner[0]=x value, corner[1]=y value
                elif index_row==BOARD_SIZE-1:
                    corners=append_element(corners,(corner[0],corner[1]+average_vertical_distance))#corner[0]=x value, corner[1]=y value
                
                #add the corners of the board
                if index_column==0 and index_row==0:
                    corners=append_element(corners,(corner[0]-average_horizontal_distance,corner[1]-average_vertical_distance))
                elif index_column==0 and index_row==BOARD_SIZE-1:
                    corners=append_element(corners,(corner[0]-average_horizontal_distance,corner[1]+average_vertical_distance))
                elif index_column==BOARD_SIZE-1 and index_row==0:
                    corners=append_element(corners,(corner[0]+average_horizontal_distance,corner[1]-average_vertical_distance))
                elif index_column==BOARD_SIZE-1 and index_row==BOARD_SIZE-1:
                    corners=append_element(corners,(corner[0]+average_horizontal_distance,corner[1]+average_vertical_distance))
    #resort the list
    corners = corners[corners[:, 0, 0].argsort()]
    #print(corners)
    return corners


def get_other_corners(corners,image):
    global BOARD_SIZE,corners_to_be_found
    #order: from top left to bottom right, row by row
    corners = corners[corners[:, 0, 0].argsort()] #sort per column
    
    tuple_kolom=()
    list_tuples_corners=[]
    for i in range(corners_to_be_found):
        for f in range(corners_to_be_found): #order: from top left to bottom right, row by row)
            tuple_kolom+=((corners[i][0][0],corners[i][0][1]),)
        list_tuples_corners.append(tuple_kolom)
    #print(list_tuples_corners)
    list_tuples_corners:list[tuple[tuple[int,int]]]

    (average_horizontal_distance_column,average_vertical_distance_column),(average_horizontal_distance_row,average_vertical_distance_row)=determine_average_distances(list_tuples_corners,corners)

    list_tuples_corners=extrapolate_other_corners(list_tuples_corners,corners,average_horizontal_distance_column,average_vertical_distance_column,average_horizontal_distance_row,average_vertical_distance_row)


    for index,i in enumerate(corners):
        print("hoek"+str(index+1)+":",i)#type=numpy.ndarray

    return list_tuples_corners

if __name__ == "__main__":
    number_of_corners=(corners_to_be_found,corners_to_be_found)
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
        #corners=get_other_corners(corners,img)
        print("corners:",corners)
        #corners=np.unique(corners,axis=0)
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, number_of_corners, corners,ret)
        cv2.namedWindow("Chessboard", cv2.WINDOW_NORMAL)
        cv2.imshow('Chessboard',img)
        cv2.waitKey(0)
    else:
        print("No chessboard detected")
    cv2.destroyAllWindows()
