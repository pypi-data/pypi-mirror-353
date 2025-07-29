import cv2
import os
import torch
import numpy as np

# from testing.test2 import bounding_boxes
from .trainer import SimpleCNN

class ColorDetector:
    """Color-based object detection using both color filtering and contour analysis"""

    def __init__(self, color_range):
        self.color_range = color_range  # Expecting RGB range

    def filter_color(self, frame):
        """Filter frame using RGB values"""
        mask = cv2.inRange(frame, self.color_range[0], self.color_range[1])
        filtered = cv2.bitwise_and(frame, frame, mask=mask)
        return filtered, mask

    def get_bounding_boxes(self, frame):
        """Find bounding boxes using contours around detected colors"""
        _, mask = self.filter_color(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = []
        for contour in contours:
            # print(cv2.contourArea(contour))
            if cv2.contourArea(contour) > 500:  # Ignore small artifacts
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))  # Store bounding box coordinates

        return bounding_boxes

    def extract_rois(self, frame, target_size=(128, 128)):
        """Extract and resize detected ROI regions"""
        bounding_boxes = self.get_bounding_boxes(frame)
        if bounding_boxes:
            rois = [cv2.resize(frame[y:y+h, x:x+w], target_size) for x, y, w, h in bounding_boxes]
            return rois  # Return resized ROIs
        return []

class RBOT:
    """Main RBOT tracking system"""

    def __init__(self, model_path, color_range):
        self.color_detector = ColorDetector(color_range)
        self.model = SimpleCNN()
        self.load_model(model_path)  # Load the trained model instead of training

    def load_model(self, model_path):
        """Load a pretrained model"""
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))
            self.model.eval()
            print(f"Pretrained model loaded from {model_path}")
        else:
            print(f"No model found at {model_path}")

    def detect_object(self, frame, target_size=(128, 128)):
        """Run detection pipeline and return resized ROI images"""
        rois = self.color_detector.extract_rois(frame, target_size)
        bounding_boxes = self.color_detector.get_bounding_boxes(frame)
        return rois, bounding_boxes  # List of resized ROIs

    def get_object(self, frame, target_size=(128, 128)):
        """Run inference on detected ROIs and return predictions"""
        rois, bounding_boxes = self.detect_object(frame, target_size)

        predictions = []
        for roi in rois:
            roi_tensor = torch.tensor(roi, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)  # Convert to tensor
            roi_tensor = roi_tensor / 255.0  # Normalize

            with torch.no_grad():  # Disable gradients for inference
                output = self.model(roi_tensor)
                predictions.append(output.item())  # Extract prediction
        if predictions:
            return rois[np.argmax(predictions)], bounding_boxes[np.argmax(predictions)]  # List of confidence scores per ROI
        return "Object not detected", "Object not detected"

    def track_object(self, frame, color, width, target_size=(128, 128), x_offset=15, y_offset=15):
        ROI, bounding_box = self.get_object(frame, target_size)
        if not isinstance(ROI, str):
            bounding_box_frame = cv2.rectangle(frame, (bounding_box[0]-x_offset, bounding_box[1]-y_offset), (bounding_box[2]+bounding_box[0]+x_offset, bounding_box[3]+bounding_box[1]+y_offset), color, width)
            return bounding_box_frame
        return frame