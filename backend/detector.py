"""YOLO-based person detection module."""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class Detection:
    """Single detection result."""
    
    def __init__(self, x1: float, y1: float, x2: float, y2: float, confidence: float):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.confidence = confidence
        self.centroid_x = (x1 + x2) / 2
        self.centroid_y = (y1 + y2) / 2
        self.width = x2 - x1
        self.height = y2 - y1
    
    def __repr__(self):
        return f"Detection(box=({self.x1:.1f},{self.y1:.1f},{self.x2:.1f},{self.y2:.1f}), conf={self.confidence:.2f})"


class PersonDetector:
    """YOLO-based person detector."""
    
    def __init__(self, model_size: str = 'nano', device: str = 'auto', confidence: float = 0.5):
        """
        Initialize YOLO detector.
        
        Args:
            model_size: 'nano', 'small', 'medium', 'large'
            device: 'cpu', 'gpu', 'auto'
            confidence: Confidence threshold (0.0-1.0)
        """
        self.model_size = model_size
        self.device = device
        self.confidence = confidence
        
        model_name = f'yolov8{model_size[0]}.pt'
        logger.info(f"Loading YOLO model: {model_name}")
        self.model = YOLO(model_name)
        self.model.to(device)
        logger.info(f"YOLO {model_size} loaded successfully")
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect persons in frame."""
        if frame is None or frame.size == 0:
            return []
        
        try:
            results = self.model(frame, conf=self.confidence, verbose=False)
            detections = []
            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    if int(box.cls[0]) == 0:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        detections.append(Detection(x1, y1, x2, y2, conf))
            return detections
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def set_confidence(self, confidence: float):
        """Update confidence threshold."""
        self.confidence = max(0.0, min(1.0, confidence))
        logger.info(f"Confidence threshold updated to {self.confidence}")
    
    def warmup(self, num_frames: int = 5):
        """Warmup GPU/model with dummy frames."""
        logger.info(f"Warming up detector with {num_frames} frames...")
        dummy_frame = np.zeros((640, 480, 3), dtype=np.uint8)
        for _ in range(num_frames):
            self.detect(dummy_frame)
        logger.info("Detector warmup complete")
