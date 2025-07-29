import os
import cv2
import customtkinter as ctk
from datetime import datetime
import threading

class DataCollector(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RBOT Data Collector")
        self.geometry("400x250")

        self.dataset_dir_var = ctk.StringVar()
        self.object_name_var = ctk.StringVar()
        self.cap = cv2.VideoCapture(0)  # Open webcam feed

        # UI Elements
        self.label_dir = ctk.CTkLabel(self, text="Enter Dataset Directory:")
        self.label_dir.pack(pady=5)

        self.entry_dir = ctk.CTkEntry(self, textvariable=self.dataset_dir_var)
        self.entry_dir.pack(pady=5)

        self.label_obj = ctk.CTkLabel(self, text="Enter Object Name:")
        self.label_obj.pack(pady=5)

        self.entry_obj = ctk.CTkEntry(self, textvariable=self.object_name_var)
        self.entry_obj.pack(pady=5)

        self.capture_button = ctk.CTkButton(self, text="Capture Object Image", command=self.capture_object)
        self.capture_button.pack(pady=5)

        self.bg_button = ctk.CTkButton(self, text="Take Background Picture", command=self.capture_background)
        self.bg_button.pack(pady=5)

        # Start the webcam feed in a separate thread
        threading.Thread(target=self.display_webcam, daemon=True).start()

    def get_dataset_dir(self):
        """Retrieve dataset directory from input"""
        dataset_dir = self.dataset_dir_var.get().strip()
        if not dataset_dir:
            print("Error: Please specify a dataset directory.")
            return None
        os.makedirs(dataset_dir, exist_ok=True)
        return dataset_dir

    def capture_object(self):
        dataset_dir = self.get_dataset_dir()
        if not dataset_dir:
            return

        object_name = self.object_name_var.get().strip()
        if not object_name:
            print("Error: Please enter an object name.")
            return

        object_dir = os.path.join(dataset_dir, object_name)
        os.makedirs(object_dir, exist_ok=True)

        self.save_image(object_dir)

    def capture_background(self):
        dataset_dir = self.get_dataset_dir()
        if dataset_dir:
            background_dir = os.path.join(dataset_dir, "background")
            os.makedirs(background_dir, exist_ok=True)
            self.save_image(background_dir)

    def save_image(self, save_dir):
        """Saves the current webcam frame when button is clicked"""
        ret, frame = self.cap.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = os.path.join(save_dir, f"{timestamp}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"Saved: {img_path}")
        else:
            print("Failed to capture image.")

    def display_webcam(self):
        """Continuously displays webcam feed in a separate OpenCV window"""
        while True:
            ret, frame = self.cap.read()
            if ret:
                cv2.imshow("Live Webcam Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def collectData(self):
        """Starts the GUI for collecting data."""
        self.mainloop()

# Usage
if __name__ == "__main__":
    collector = DataCollector()
    collector.collectData()
