import cv2
import numpy as np
from cvzone.ColorModule import ColorFinder  # part of cvzone

class ColorRangeSelector:
    def __init__(self, window_name="HSV Selector"):
        self.window_name = window_name
        self.color_finder = ColorFinder(True)

    def select_color_range(self, color="blue"):
        cap = cv2.VideoCapture(0)
        lower_bound, upper_bound = np.array([0, 0, 0]), np.array([179, 255, 255])

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            imgColor, mask = self.color_finder.update(frame, color)
            cv2.imshow("Frame", imgColor)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Exit condition
                break

        cap.release()
        cv2.destroyAllWindows()
        return lower_bound, upper_bound  # Ensure values are returned

# Run it
if __name__ == "__main__":
    selector = ColorRangeSelector()
    lower, upper = selector.select_color_range()
    print("Final HSV Range:")
    print("Lower:", lower)
    print("Upper:", upper)
