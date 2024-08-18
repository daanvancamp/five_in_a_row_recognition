
import cv2
import numpy as np

BOARD_SIZE = 15  # Dit geeft het aantal vakjes op het bord aan, wat betekent dat er 16x16 hoeken zijn.
corners_to_be_found = BOARD_SIZE - 1  # Dit is het aantal hoeken tussen de vakjes (14x14)

def draw_point_and_show(image, point, window_name="Corners",wait_key=1):
    """Tekent een cirkel op het opgegeven punt op de afbeelding en toont deze."""
    color = (0, 0, 255)  # Rood in BGR
    radius = 10
    thickness = -1
    point = (int(point[0]), int(point[1]))
    cv2.circle(image, point, radius, color, thickness)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, image)
    cv2.waitKey(wait_key)

def calculate_euclidean_distance(p1, p2):
    """Berekent de Euclidische afstand tussen twee punten."""
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def determine_average_distances(corners):
    """Berekent de gemiddelde horizontale en verticale afstanden tussen punten."""
    corners = corners.reshape((corners_to_be_found, corners_to_be_found, 2))  # Reshape to 2D grid of (x, y) points
    
    horizontal_distances = []
    vertical_distances = []

    # Loop door de hoekpunten (14x14 grid)
    for i in range(corners_to_be_found):
        for j in range(corners_to_be_found):
            p1 = corners[i, j]

            # Voeg horizontale afstanden toe
            if j + 1 < corners_to_be_found:
                p2 = corners[i, j + 1]
                horizontal_distances.append(calculate_euclidean_distance(p1, p2))

            # Voeg verticale afstanden toe
            if i + 1 < corners_to_be_found:
                p3 = corners[i + 1, j]
                vertical_distances.append(calculate_euclidean_distance(p1, p3))

    # Bereken de gemiddelde afstanden
    avg_horizontal_distance = np.mean(horizontal_distances)
    avg_vertical_distance = np.mean(vertical_distances)

    return avg_horizontal_distance, avg_vertical_distance

def extrapolate_other_corners(corners, avg_distances):
    """Extrapoleert de buitenste hoeken van het schaakbord."""
    avg_horizontal, avg_vertical = avg_distances

    # Huidig aantal hoeken is 14x14 (196 hoeken), we moeten naar 16x16 (256 hoeken)
    complete_corners = np.zeros((BOARD_SIZE + 1, BOARD_SIZE + 1, 2), dtype=np.float32)
    complete_corners[1:-1, 1:-1] = corners.reshape((corners_to_be_found, corners_to_be_found, 2))

    # Extrapoleer de rechterkolom en onderrij
    for i in range(1, BOARD_SIZE):
        complete_corners[i, -1] = [complete_corners[i, -2, 0] + avg_horizontal, complete_corners[i, -2, 1]]

    for j in range(1, BOARD_SIZE):
        complete_corners[-1, j] = [complete_corners[-2, j, 0], complete_corners[-2, j, 1] + avg_vertical]

    # Extrapoleer de linkerkolom en bovenrij
    for i in range(1, BOARD_SIZE):
        complete_corners[i, 0] = [complete_corners[i, 1, 0] - avg_horizontal, complete_corners[i, 1, 1]]

    for j in range(1, BOARD_SIZE):
        complete_corners[0, j] = [complete_corners[1, j, 0], complete_corners[1, j, 1] - avg_vertical]

    # Extrapoleer de hoeken
    complete_corners[0, 0] = [complete_corners[1, 1, 0] - avg_horizontal, complete_corners[1, 1, 1] - avg_vertical]
    complete_corners[0, -1] = [complete_corners[1, -2, 0] + avg_horizontal, complete_corners[1, -2, 1] - avg_vertical]
    complete_corners[-1, 0] = [complete_corners[-2, 1, 0] - avg_horizontal, complete_corners[-2, 1, 1] + avg_vertical]
    complete_corners[-1, -1] = [complete_corners[-2, -2, 0] + avg_horizontal, complete_corners[-2, -2, 1] + avg_vertical]

    return complete_corners

def calculate_cell_centers(corners):
    """Berekent de middelpunten van alle cellen in het schaakbord."""
    centers = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            p1 = corners[i, j]
            p2 = corners[i, j + 1]
            p3 = corners[i + 1, j]
            p4 = corners[i + 1, j + 1]
            center_x = (p1[0] + p2[0] + p3[0] + p4[0]) / 4
            center_y = (p1[1] + p2[1] + p3[1] + p4[1]) / 4
            centers.append((center_x, center_y))
    return np.array(centers)

def main():
    number_of_corners = (corners_to_be_found, corners_to_be_found)
    
    # Laad de afbeelding
    img = cv2.imread(r'./testopstellingen/bord10.jpg')

    # Converteer naar grijswaarden
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        raise Exception(f"Check the image path: {e}")

    # Zoek de hoeken van het schaakbord (14x14 grid)
    ret, corners = cv2.findChessboardCorners(gray, number_of_corners, None)
    
    # Als de hoeken van het schaakbord zijn gedetecteerd
    if ret == True:
        print("Chessboard detected")
        
        # Verfijn de hoeken voor betere nauwkeurigheid
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), 
                                   criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        
        # Bereken gemiddelde afstanden
        avg_distances = determine_average_distances(corners)
        
        # Extrapoleer de ontbrekende buitenste hoeken
        all_corners = extrapolate_other_corners(corners, avg_distances)
        
        # Teken het schaakbord met alle hoeken
        img_with_corners = img.copy()
        img_with_corners = cv2.drawChessboardCorners(img_with_corners, (BOARD_SIZE + 1, BOARD_SIZE + 1), all_corners.reshape(-1, 1, 2), ret)
        cv2.namedWindow("Chessboard", cv2.WINDOW_NORMAL)
        cv2.imshow('Chessboard', img_with_corners)
        cv2.waitKey(0)

        # Bereken de middelpunten van de cellen
        cell_centers = calculate_cell_centers(all_corners)

        # Teken de middelpunten op een nieuwe afbeelding
        img_with_centers = img.copy()
        for index,center in enumerate(cell_centers):
            if index == len(cell_centers) - 1:
                draw_point_and_show(img_with_centers, tuple(center), window_name="Cell Centers",wait_key=0)
            else:
                draw_point_and_show(img_with_centers, tuple(center), window_name="Cell Centers")

    else:
        print("No chessboard detected")
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
