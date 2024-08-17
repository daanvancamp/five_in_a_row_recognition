# import required libraries
from operator import index
import cv2
from math import sqrt
import numpy as np

BOARD_SIZE=15
corners_to_be_found=BOARD_SIZE-1

def draw_point_and_show(image,point):
    color = (0, 0, 255)  # Rood in BGR

    radius = 10
    thickness = -1  

    cv2.circle(image, point, radius, color, thickness)
    cv2.namedWindow("Corners", cv2.WINDOW_NORMAL)

    cv2.imshow("Corners", image)  

def determine_average_distances(corners)->tuple[int,int]:
    aantal=0
    list_x_values_column=[]
    list_y_values_column=[]
    for i in range(corners_to_be_found):

        list_x_values_column.append(corner[0])#=x value
        list_y_values_column.append(corner[1])#=y value
        for i in range(corners_to_be_found):
            pass
    average_horizontal_distance_column=(max(list_x_values_column)-min(list_x_values_column))/(corners_to_be_found)
    average_vertical_distance_column=(max(list_y_values_column)-min(list_y_values_column))/(corners_to_be_found)
    
    corners = corners[corners[0, :, 0].argsort()]#sort per row

    for corner in corners:
        list_x_values_row=[]
        list_y_values_row=[]
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


def extrapolate_other_corners(,corners,average_horizontal_distance,average_vertical_distance)->list:
    for index_column,column in enumerate():
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

    (average_horizontal_distance_column,average_vertical_distance_column),(average_horizontal_distance_row,average_vertical_distance_row)=determine_average_distances(corners)

    #list_tuples_corners=extrapolate_other_corners(list_tuples_corners,corners,average_horizontal_distance_column,average_vertical_distance_column,average_horizontal_distance_row,average_vertical_distance_row)

    for index,i in enumerate(corners):
        print("hoek"+str(index+1)+":",i)#type=numpy.ndarray

    return corners

if __name__ == "__main__":
    number_of_corners=(corners_to_be_found,corners_to_be_found)
    # read input image
    img = cv2.imread(r'./testopstellingen/bord10.jpg')

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
        corners=get_other_corners(corners,img)
        img = cv2.drawChessboardCorners(img, number_of_corners, corners,ret)
        cv2.namedWindow("Chessboard", cv2.WINDOW_NORMAL)
        cv2.imshow('Chessboard',img)
        cv2.waitKey(0)
    else:
        print("No chessboard detected")
    cv2.destroyAllWindows()


   #todo: detect middle point of each cell(square)
   #todo:use "pythagoras to calculate the closest distance between two points"