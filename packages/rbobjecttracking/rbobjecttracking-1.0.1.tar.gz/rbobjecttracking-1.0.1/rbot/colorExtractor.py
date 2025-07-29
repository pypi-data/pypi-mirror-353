import cv2
import numpy as np

class ColorRangeSelector:
    """Interactive RGB range selector using OpenCV trackbars"""

    def __init__(self, window_name="Color Range Selector"):
        self.window_name = window_name
        self.lower_bound = np.array([0, 0, 0])
        self.upper_bound = np.array([255, 255, 255])

        cv2.namedWindow(self.window_name)
        self._create_trackbars()

    def _create_trackbars(self):
        """Creates trackbars for adjusting RGB values"""
        cv2.createTrackbar("R Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("G Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("B Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("R Max", self.window_name, 255, 255, lambda x: None)
        cv2.createTrackbar("G Max", self.window_name, 255, 255, lambda x: None)
        cv2.createTrackbar("B Max", self.window_name, 255, 255, lambda x: None)

    def _update_bounds(self):
        """Updates RGB bounds based on trackbar values"""
        r_min = cv2.getTrackbarPos("R Min", self.window_name)
        g_min = cv2.getTrackbarPos("G Min", self.window_name)
        b_min = cv2.getTrackbarPos("B Min", self.window_name)
        r_max = cv2.getTrackbarPos("R Max", self.window_name)
        g_max = cv2.getTrackbarPos("G Max", self.window_name)
        b_max = cv2.getTrackbarPos("B Max", self.window_name)

        self.lower_bound = np.array([b_min, g_min, r_min])  # OpenCV uses BGR order
        self.upper_bound = np.array([b_max, g_max, r_max])

    def select_color_range(self, capture_source=0):
        """Starts interactive RGB selection"""
        cap = cv2.VideoCapture(capture_source)

        while True:
            _, frame = cap.read()

            self._update_bounds()
            mask = cv2.inRange(frame, self.lower_bound, self.upper_bound)
            filtered = cv2.bitwise_and(frame, frame, mask=mask)  # Preserve colors

            cv2.imshow("Original", frame)
            cv2.imshow("Filtered Colors", filtered)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print(f"Selected RGB Range - Lower: {self.lower_bound}, Upper: {self.upper_bound}")
                break

        cap.release()
        cv2.destroyAllWindows()
        return self.lower_bound, self.upper_bound

# Example usage
if __name__ == "__main__":
    selector = ColorRangeSelector()
    lower, upper = selector.select_color_range()
    print(f"Final RGB Range - Lower: {lower}, Upper: {upper}")