import cv2
import os
import torch
import numpy as np
import ast
from .trainer import EnhancedObjectConfidenceCNN  # Ensure this import is correct
import torch.quantization

# Enable GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ColorDetector:
    """Color-based object detection using HSV filtering and contour analysis."""
    def __init__(self, color_range_str):
        """Initialize with a color range string and convert it into usable values."""
        self.color_range = self.parse_color_range(color_range_str)

    def parse_color_range(self, color_range_str):
        """Convert the color range string to a usable dictionary."""
        color_values = ast.literal_eval(color_range_str)
        return color_values

    def filter_color(self, frame):
        """Apply color filtering using HSV values."""
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([self.color_range['hmin'], self.color_range['smin'], self.color_range['vmin']])
        upper_bound = np.array([self.color_range['hmax'], self.color_range['smax'], self.color_range['vmax']])
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        return mask

    def get_bounding_boxes(self, frame, minimum_contour_size, maximum_contour_size):
        """Find bounding boxes using contours around detected colors."""
        mask = self.filter_color(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = []
        for contour in contours:
            if maximum_contour_size > cv2.contourArea(contour) > minimum_contour_size:  # Ignore small artifacts
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))  # Store bounding box coordinates

        return bounding_boxes

    def extract_rois(self, frame, minimum_contour_size, maximum_contour_size, target_size=(128, 128), x_offset=30, y_offset=30):
        """Extract and resize detected ROI regions."""
        bounding_boxes = self.get_bounding_boxes(frame, minimum_contour_size, maximum_contour_size)
        height, width = frame.shape[:2]  # Get image dimensions

        rois = [cv2.resize(frame[max(0, y - y_offset) : min(height, y + h + y_offset),max(0, x - x_offset) : min(width, x + w + x_offset)], target_size)for x, y, w, h in bounding_boxes] if bounding_boxes else []
        return rois, bounding_boxes

class RBOT:
    def __init__(self, hsvValues, image_size, minimum_contour_size=500, maximum_contour_size=10000, minimum_confidence=0.8, model_path="classifier.pth", use_cuda=False, quantized_model=False):
        global device
        if not use_cuda:
            device = torch.device("cpu")

        self.image_size = image_size  # ✅ Move this line UP before load_model()
        self.color_detector = ColorDetector(hsvValues)
        self.model = EnhancedObjectConfidenceCNN(self.image_size).to(device)  # Move model to GPU

        self.load_model(model_path, quantized_model)  # ✅ Now it correctly refers to self.image_size

        self.minimum_contour_size = minimum_contour_size
        self.maximum_contour_size = maximum_contour_size
        self.minimum_confidence = minimum_confidence

    def load_model(self, model_path, quantized=False):
        """Loads a pretrained model, handling both standard and quantized models correctly."""
        print(f"📥 Loading model from {model_path}")

        self.model = EnhancedObjectConfidenceCNN(self.image_size)  # Initialize model normally

        # Load model parameters
        model_state = torch.load(model_path, map_location=device)

        if quantized:
            print("⚡ Loading quantized model...")
            self.model = torch.quantization.quantize_dynamic(self.model, {torch.nn.Linear}, dtype=torch.qint8)

        self.model.load_state_dict(model_state)
        self.model.to(device)
        self.model.eval()

        print("✅ Model loaded successfully!")

    def detect_object(self, frame, target_size=(128, 128), x_offset=30, y_offset=30):
        """Run detection pipeline and return resized ROI images."""
        rois, bounding_boxes = self.color_detector.extract_rois(frame, minimum_contour_size=self.minimum_contour_size, maximum_contour_size=self.maximum_contour_size, target_size=target_size, x_offset=x_offset, y_offset=y_offset)
        return rois, bounding_boxes

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
            return bounding_box_frame, bounding_box

        return frame, bounding_box
