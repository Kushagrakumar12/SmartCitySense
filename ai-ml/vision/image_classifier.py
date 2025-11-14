"""
Image Classification and Event Detection
Uses YOLOv8 for object detection and event classification from user-uploaded images
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO

from utils.logger import get_logger
from utils.schemas import (
    EventType, SeverityLevel, DetectedObject,
    VisionAnalysisResponse
)
from config.config import config

logger = get_logger("image_classifier")


class ImageClassifier:
    """
    Image classification and event detection using YOLOv8
    
    Features:
    - Object detection (fallen trees, vehicles, people, etc.)
    - Event type classification
    - Severity estimation
    - Description generation
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize image classifier
        
        Args:
            model_path: Path to YOLO model weights (default: from config)
        """
        self.model_path = model_path or config.vision.yolo_model_path
        self.device = config.device
        self.model = None
        self.confidence_threshold = config.vision.confidence_threshold
        self.iou_threshold = config.vision.iou_threshold
        
        # Event mapping based on detected objects
        self.event_mappings = self._initialize_event_mappings()
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            model_path = Path(self.model_path)
            
            # Download model if not exists
            if not model_path.exists():
                logger.info(f"Model not found at {model_path}, downloading YOLOv8{config.vision.yolo_model_size}...")
                model_path.parent.mkdir(parents=True, exist_ok=True)
                self.model = YOLO(f'yolov8{config.vision.yolo_model_size}.pt')
                # Save for future use
                self.model.save(str(model_path))
            else:
                logger.info(f"Loading model from {model_path}")
                self.model = YOLO(str(model_path))
            
            # Move model to appropriate device
            self.model.to(self.device)
            logger.success(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _initialize_event_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize mappings from detected objects to event types
        
        Returns:
            Dictionary mapping object classes to event information
        """
        return {
            # Traffic-related
            "car": {"event_type": EventType.TRAFFIC, "severity": SeverityLevel.LOW},
            "truck": {"event_type": EventType.TRAFFIC, "severity": SeverityLevel.MEDIUM},
            "bus": {"event_type": EventType.TRAFFIC, "severity": SeverityLevel.MEDIUM},
            "motorcycle": {"event_type": EventType.TRAFFIC, "severity": SeverityLevel.LOW},
            "traffic light": {"event_type": EventType.TRAFFIC, "severity": SeverityLevel.LOW},
            
            # Obstructions
            "tree": {"event_type": EventType.OBSTRUCTION, "severity": SeverityLevel.HIGH},
            "pothole": {"event_type": EventType.CIVIC_ISSUE, "severity": SeverityLevel.MEDIUM},
            "debris": {"event_type": EventType.OBSTRUCTION, "severity": SeverityLevel.MEDIUM},
            
            # Water/Flooding
            "water": {"event_type": EventType.FLOODING, "severity": SeverityLevel.HIGH},
            "flood": {"event_type": EventType.FLOODING, "severity": SeverityLevel.CRITICAL},
            
            # Fire/Emergency
            "fire": {"event_type": EventType.FIRE, "severity": SeverityLevel.CRITICAL},
            "smoke": {"event_type": EventType.FIRE, "severity": SeverityLevel.HIGH},
            
            # People/Protests
            "person": {"event_type": EventType.PROTEST, "severity": SeverityLevel.MEDIUM},
            "crowd": {"event_type": EventType.PROTEST, "severity": SeverityLevel.HIGH},
            
            # Construction
            "construction": {"event_type": EventType.CONSTRUCTION, "severity": SeverityLevel.MEDIUM},
            "excavator": {"event_type": EventType.CONSTRUCTION, "severity": SeverityLevel.MEDIUM},
        }
    
    def classify_image(
        self,
        image_path,
        save_debug: bool = False
    ) -> VisionAnalysisResponse:
        """
        Classify an image and detect events
        
        Args:
            image_path: Can be:
                - str: Path or URL to image file
                - PIL.Image.Image: PIL Image object
                - np.ndarray: Numpy array
            save_debug: Whether to save annotated debug image
        
        Returns:
            VisionAnalysisResponse with detected events and objects
        """
        start_time = time.time()
        
        try:
            # Load image
            image = self._load_image(image_path)
            
            # Run detection
            results = self.model.predict(
                image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )[0]
            
            # Extract detections
            detected_objects = self._parse_detections(results)
            
            # Classify event type
            event_type, severity = self._classify_event(detected_objects)
            
            # Generate description
            description = self._generate_description(event_type, detected_objects)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(detected_objects)
            
            # Generate tags
            tags = self._generate_tags(event_type, detected_objects)
            
            # Save debug image if requested
            if save_debug and config.save_debug_images:
                self._save_debug_image(image_path, results, event_type)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"Image classified: {event_type.value} (confidence: {confidence:.2f})")
            
            return VisionAnalysisResponse(
                event_type=event_type,
                description=description,
                confidence=confidence,
                severity=severity,
                detected_objects=detected_objects,
                tags=tags,
                processing_time_ms=processing_time,
                model_version=f"yolov8{config.vision.yolo_model_size}"
            )
            
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            raise
    
    def _load_image(self, image_path) -> np.ndarray:
        """
        Load image from file path, URL, or PIL Image object
        
        Args:
            image_path: Can be:
                - str: file path or URL
                - PIL.Image.Image: PIL Image object
                - np.ndarray: numpy array
        
        Returns:
            Image as numpy array
        """
        try:
            # Handle PIL Image object
            if isinstance(image_path, Image.Image):
                image = np.array(image_path.convert('RGB'))
            
            # Handle numpy array
            elif isinstance(image_path, np.ndarray):
                image = image_path
            
            # Handle string (file path or URL)
            elif isinstance(image_path, str):
                if image_path.startswith(('http://', 'https://')):
                    # Download image from URL
                    import requests
                    from io import BytesIO
                    response = requests.get(image_path, timeout=10)
                    pil_image = Image.open(BytesIO(response.content))
                    image = np.array(pil_image.convert('RGB'))
                else:
                    # Load from local file
                    image = cv2.imread(image_path)
                    if image is None:
                        raise ValueError(f"Failed to load image from {image_path}")
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                raise TypeError(f"Unsupported image type: {type(image_path)}")
            
            # Resize if too large
            if max(image.shape[:2]) > config.vision.max_image_size:
                scale = config.vision.max_image_size / max(image.shape[:2])
                new_size = (int(image.shape[1] * scale), int(image.shape[0] * scale))
                image = cv2.resize(image, new_size)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise
    
    def _parse_detections(self, results) -> List[DetectedObject]:
        """Parse YOLO detection results"""
        detected_objects = []
        
        if results.boxes is not None:
            for box in results.boxes:
                class_id = int(box.cls[0])
                class_name = results.names[class_id]
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()
                
                detected_objects.append(DetectedObject(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=bbox
                ))
        
        return detected_objects
    
    def _classify_event(
        self,
        detected_objects: List[DetectedObject]
    ) -> Tuple[EventType, SeverityLevel]:
        """
        Classify event type based on detected objects
        
        Returns:
            Tuple of (EventType, SeverityLevel)
        """
        if not detected_objects:
            return EventType.OTHER, SeverityLevel.LOW
        
        # Score each event type
        event_scores = {}
        severity_scores = {}
        
        for obj in detected_objects:
            class_name = obj.class_name.lower()
            
            # Check if object maps to known event
            if class_name in self.event_mappings:
                mapping = self.event_mappings[class_name]
                event_type = mapping["event_type"]
                severity = mapping["severity"]
                
                # Accumulate scores weighted by confidence
                if event_type not in event_scores:
                    event_scores[event_type] = 0
                    severity_scores[event_type] = []
                
                event_scores[event_type] += obj.confidence
                severity_scores[event_type].append(severity)
        
        # Determine most likely event type
        if event_scores:
            event_type = max(event_scores, key=event_scores.get)
            # Use highest severity detected
            severities = severity_scores[event_type]
            severity_order = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
            severity = max(severities, key=lambda s: severity_order.index(s))
        else:
            # Default based on heuristics
            event_type, severity = self._heuristic_classification(detected_objects)
        
        return event_type, severity
    
    def _heuristic_classification(
        self,
        detected_objects: List[DetectedObject]
    ) -> Tuple[EventType, SeverityLevel]:
        """Fallback heuristic classification"""
        # Count vehicles for traffic
        vehicle_classes = {"car", "truck", "bus", "motorcycle"}
        vehicle_count = sum(1 for obj in detected_objects if obj.class_name.lower() in vehicle_classes)
        
        if vehicle_count > 10:
            return EventType.TRAFFIC, SeverityLevel.HIGH
        elif vehicle_count > 5:
            return EventType.TRAFFIC, SeverityLevel.MEDIUM
        
        # Count people for protests/crowds
        person_count = sum(1 for obj in detected_objects if obj.class_name.lower() == "person")
        if person_count > 20:
            return EventType.PROTEST, SeverityLevel.HIGH
        elif person_count > 10:
            return EventType.PROTEST, SeverityLevel.MEDIUM
        
        return EventType.OTHER, SeverityLevel.LOW
    
    def _generate_description(
        self,
        event_type: EventType,
        detected_objects: List[DetectedObject]
    ) -> str:
        """Generate human-readable event description"""
        if not detected_objects:
            return "No significant objects detected in image"
        
        # Get most confident objects
        top_objects = sorted(detected_objects, key=lambda x: x.confidence, reverse=True)[:3]
        obj_names = [obj.class_name for obj in top_objects]
        
        # Generate description based on event type
        descriptions = {
            EventType.TRAFFIC: f"Traffic situation with {', '.join(obj_names)} detected",
            EventType.OBSTRUCTION: f"Road obstruction - {obj_names[0]} blocking path",
            EventType.FLOODING: "Flooding detected - water on road surface",
            EventType.FIRE: "Fire or smoke detected - emergency situation",
            EventType.PROTEST: f"Crowd gathering detected - {len([o for o in detected_objects if o.class_name == 'person'])} people visible",
            EventType.ACCIDENT: "Possible accident scene detected",
            EventType.CIVIC_ISSUE: f"Civic issue detected - {', '.join(obj_names)}",
            EventType.CONSTRUCTION: "Construction activity detected",
            EventType.POWER_OUTAGE: "Infrastructure issue detected",
        }
        
        return descriptions.get(
            event_type,
            f"Event detected with {', '.join(obj_names)}"
        )
    
    def _calculate_confidence(self, detected_objects: List[DetectedObject]) -> float:
        """Calculate overall confidence score"""
        if not detected_objects:
            return 0.0
        
        # Average of top 3 confidences
        top_confidences = sorted([obj.confidence for obj in detected_objects], reverse=True)[:3]
        return sum(top_confidences) / len(top_confidences)
    
    def _generate_tags(
        self,
        event_type: EventType,
        detected_objects: List[DetectedObject]
    ) -> List[str]:
        """Generate relevant tags"""
        tags = [event_type.value]
        
        # Add object classes as tags
        for obj in detected_objects:
            tag = obj.class_name.lower().replace(" ", "_")
            if tag not in tags:
                tags.append(tag)
        
        return tags[:10]  # Limit to 10 tags
    
    def _save_debug_image(
        self,
        image_path: str,
        results,
        event_type: EventType
    ):
        """Save annotated debug image"""
        try:
            debug_dir = Path(__file__).parent.parent / "logs" / "debug_images"
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            # Create annotated image
            annotated = results.plot()
            
            # Save with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{event_type.value}_{timestamp}.jpg"
            output_path = debug_dir / filename
            
            cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
            logger.debug(f"Debug image saved: {output_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save debug image: {e}")


if __name__ == "__main__":
    # Test image classifier
    logger.info("Testing Image Classifier...")
    
    classifier = ImageClassifier()
    logger.info("Classifier initialized successfully")
    
    print("\n" + "="*60)
    print("✅ Image Classifier Test Passed")
    print("="*60)
    print("\nTo test with an actual image:")
    print('  result = classifier.classify_image("path/to/image.jpg")')
    print('  print(result.model_dump_json(indent=2))')
