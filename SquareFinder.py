
import cv2
import numpy as np

class SquareFinder:
    # Constante parameters voor vierkantdetectie
    canny_upper_thresh = 30
    thresh_it = 30

    @staticmethod
    def find_squares(image):
        """
        Detecteert vierkanten in een afbeelding.

        Parameters:
            image (numpy.ndarray): De invoerafbeelding waarin vierkanten moeten worden gedetecteerd.

        Returns:
            list: Een lijst van vierkanten (elk vierkant wordt gerepresenteerd als een lijst van vier punten).
        """
        squares = []

        # Maak een kopie van de afbeelding om mee te werken
        img = image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Voor elke kleurcomponent in de afbeelding
        for c in range(3):
            # Splits de kleurkanalen
            ch = img[:, :, c]

            # Probeer meerdere drempelwaarden
            for l in range(SquareFinder.thresh_it):
                # Gebruik Canny bij de eerste iteratie
                if l == 0:
                    edges = cv2.Canny(ch, 0, SquareFinder.canny_upper_thresh)
                    edges = cv2.dilate(edges, None)
                else:
                    _retval, edges = cv2.threshold(ch, (l + 1) * 255 / SquareFinder.thresh_it, 255, cv2.THRESH_BINARY)

                # Vind contouren
                contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in contours:
                    # Benader het contour met een nauwkeurigheid afhankelijk van de omtrek
                    epsilon = 0.02 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)

                    # Controleer of de benaderde contour een vierkant is
                    if len(approx) == 4 and cv2.isContourConvex(approx):
                        # Controleer of het vierkant een voldoende grote oppervlakte heeft
                        if cv2.contourArea(approx) > 1000:
                            max_cosine = 0
                            for i in range(2, 5):
                                cosine = abs(SquareFinder.angle_cos(approx[i % 4], approx[i - 2], approx[i - 1]))
                                max_cosine = max(max_cosine, cosine)
                            
                            # Controleer of de maximale cosinuswaarde minder dan 0.5 is (alle hoeken dicht bij 90 graden)
                            if max_cosine < 0.5:
                                squares.append(approx)

        return squares

    @staticmethod
    def angle_cos(p0, p1, p2):
        """
        Berekent de cosinus van de hoek tussen twee vectoren met gemeenschappelijk startpunt.

        Parameters:
            p0, p1, p2: Punten die de vectoren definiëren.

        Returns:
            float: De cosinus van de hoek tussen de vectoren.
        """
        dx1, dy1 = p1[0][0] - p0[0][0], p1[0][1] - p0[0][1]
        dx2, dy2 = p2[0][0] - p0[0][0], p2[0][1] - p0[0][1]
        return (dx1 * dx2 + dy1 * dy2) / np.sqrt((dx1 ** 2 + dy1 ** 2) * (dx2 ** 2 + dy2 ** 2) + 1e-10)

# Voorbeeld van gebruik (commentaar verwijderen om uit te voeren):
# if __name__ == "__main__":
#     image = cv2.imread('path_to_image.jpg')
#     squares = SquareFinder.find_squares(image)
#     for square in squares:
#         cv2.polylines(image, [square], True, (0, 255, 0), 2)
#     cv2.imshow('Squares', image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
