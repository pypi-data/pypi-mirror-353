import cv2
import os
import torch
import numpy as np
from cvzone.ColorModule import ColorFinder
from .trainer import EnhancedObjectConfidenceCNN  # Ensure this import is correct

# Enable GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ColorDetector:
    """Color-based object detection using both color filtering and contour analysis."""
    def __init__(self, color_range):
        self.color_range = color_range
        self.color_finder = ColorFinder(False)  # Expecting RGB range

    def filter_color(self, frame):
        """Filter frame using HSV values."""
        imgColor, mask = self.color_finder.update(frame, self.color_range)
        return imgColor, mask

    def get_bounding_boxes(self, frame, minimum_contour_size):
        """Find bounding boxes using contours around detected colors."""
        _, mask = self.filter_color(frame)
        mask = np.array(mask, dtype=np.uint8)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = []
        for contour in contours:
            if cv2.contourArea(contour) > minimum_contour_size:  # Ignore small artifacts
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))  # Store bounding box coordinates

        return bounding_boxes

    def extract_rois(self, frame, minimum_contour_size, target_size=(128, 128), x_offset=30, y_offset=30):
        """Extract and resize detected ROI regions."""
        bounding_boxes = self.get_bounding_boxes(frame, minimum_contour_size=minimum_contour_size)
        rois = [cv2.resize(frame[y-y_offset:y+h+y_offset, x-x_offset:x+w+x_offset], target_size) for x, y, w, h in bounding_boxes] if bounding_boxes else []
        return rois, bounding_boxes

class RBOT:
    """Main RBOT tracking system."""
    def __init__(self, hsvValues, image_size, minimum_contour_size=500, minimum_confidence=0.8, model_path="classifier.pth", use_cuda=False):
        global device
        if not use_cuda:
            device = torch.device("cpu")
        self.color_detector = ColorDetector(hsvValues)
        self.model = EnhancedObjectConfidenceCNN(image_size).to(device)  # Move model to GPU
        self.load_model(model_path)  # Load the trained model instead of training
        self.image_size = image_size
        self.minimum_contour_size = minimum_contour_size
        self.minimum_confidence = minimum_confidence

    def load_model(self, model_path):
        """Load a pretrained model."""
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=device))  # Ensure model loads on GPU
            self.model.eval()
            print(f"✅ Pretrained model loaded from {model_path}")
        else:
            raise FileNotFoundError(f"❌ No model found at {model_path}")

    def detect_object(self, frame, target_size=(128, 128), x_offset=30, y_offset=30):
        """Run detection pipeline and return resized ROI images."""
        rois, bounding_boxes = self.color_detector.extract_rois(frame, target_size=target_size, minimum_contour_size=self.minimum_contour_size, x_offset=x_offset, y_offset=y_offset)
        return rois, bounding_boxes  # List of resized ROIs

    def get_object(self, frame, target_size=(128, 128), x_offset=30, y_offset=30):
        """Run inference on detected ROIs and return predictions."""
        rois, bounding_boxes = self.detect_object(frame, target_size, x_offset=x_offset, y_offset=y_offset)

        predictions = []
        for roi in rois:
            roi_tensor = torch.tensor(roi, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(device)  # Convert to tensor & move to GPU
            roi_tensor /= 255.0  # Normalize

            with torch.no_grad():  # Disable gradients for inference
                output = self.model(roi_tensor)  # Get model predictions
                confidence_scores = output.squeeze().cpu().numpy()  # Extract scores for object and not_object
                predictions.append(confidence_scores)

        if predictions:
            best_idx = np.argmax([pred[0] for pred in predictions])  # Select the highest object confidence
            # print(predictions[best_idx])

            best_prediction = predictions[best_idx]

            if (best_prediction[0] > best_prediction[1]) and best_prediction[0] > self.minimum_confidence:  # If object confidence is higher
                return rois[best_idx], bounding_boxes[best_idx]

        return "Object not detected", "Object not detected"

    def track_object(self, frame, color, width, x_offset=30, y_offset=30, bx_offset=15, by_offset=15):
        """Tracks object using bounding box visualization."""
        ROI, bounding_box = self.get_object(frame, self.image_size, x_offset=x_offset, y_offset=y_offset)
        if not isinstance(ROI, str):
            x, y, w, h = bounding_box
            bounding_box_frame = cv2.rectangle(frame, (x-bx_offset, y-by_offset), (x+w+bx_offset, y+h+by_offset), color, width)
            return bounding_box_frame

        return frame
