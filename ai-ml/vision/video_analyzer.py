"""
Video Analysis and Event Detection
Extracts key frames from videos and analyzes them for event detection
"""

import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import cv2
import numpy as np
from datetime import datetime

from utils.logger import get_logger
from utils.schemas import VisionAnalysisResponse, DetectedObject
from config.config import config
from .image_classifier import ImageClassifier

logger = get_logger("video_analyzer")


class VideoAnalyzer:
    """
    Video analysis for event detection
    
    Features:
    - Key frame extraction
    - Multi-frame analysis
    - Temporal event detection
    - Aggregated results from multiple frames
    """
    
    def __init__(self, image_classifier: Optional[ImageClassifier] = None):
        """
        Initialize video analyzer
        
        Args:
            image_classifier: ImageClassifier instance (creates new if None)
        """
        self.classifier = image_classifier or ImageClassifier()
        self.max_duration = config.vision.max_video_duration
        self.max_frames = config.vision.max_video_frames
    
    def analyze_video(
        self,
        video_path: str,
        sample_rate: Optional[int] = None,
        save_debug: bool = False
    ) -> VisionAnalysisResponse:
        """
        Analyze video and detect events
        
        Args:
            video_path: Path or URL to video file
            sample_rate: Frame sampling rate (extract every Nth frame)
            save_debug: Whether to save debug frames
        
        Returns:
            VisionAnalysisResponse aggregated from key frames
        """
        start_time = time.time()
        
        try:
            logger.info(f"Analyzing video: {video_path}")
            
            # Extract key frames
            frames = self._extract_key_frames(video_path, sample_rate)
            
            if not frames:
                raise ValueError("No frames extracted from video")
            
            logger.info(f"Extracted {len(frames)} key frames")
            
            # Analyze each frame
            frame_results = []
            for i, frame in enumerate(frames):
                # Save frame temporarily
                temp_path = self._save_temp_frame(frame, i)
                
                # Classify frame
                result = self.classifier.classify_image(temp_path, save_debug=False)
                frame_results.append(result)
                
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
            
            # Aggregate results
            aggregated_result = self._aggregate_results(frame_results)
            
            # Update processing time
            processing_time = (time.time() - start_time) * 1000
            aggregated_result.processing_time_ms = processing_time
            
            logger.success(f"Video analyzed: {aggregated_result.event_type.value}")
            return aggregated_result
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            raise
    
    def _extract_key_frames(
        self,
        video_path: str,
        sample_rate: Optional[int] = None
    ) -> List[np.ndarray]:
        """
        Extract key frames from video
        
        Args:
            video_path: Path to video file
            sample_rate: Frame sampling rate (auto-calculated if None)
        
        Returns:
            List of frames as numpy arrays
        """
        try:
            # Open video
            if video_path.startswith(('http://', 'https://')):
                # Download video first
                video_path = self._download_video(video_path)
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Failed to open video: {video_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video properties: {fps} FPS, {total_frames} frames, {duration:.1f}s duration")
            
            # Check duration limit
            if duration > self.max_duration:
                logger.warning(f"Video duration ({duration:.1f}s) exceeds limit ({self.max_duration}s)")
                total_frames = int(self.max_duration * fps)
            
            # Calculate sample rate if not provided
            if sample_rate is None:
                sample_rate = max(1, total_frames // self.max_frames)
            
            logger.info(f"Extracting frames with sample rate: {sample_rate}")
            
            # Extract frames
            frames = []
            frame_count = 0
            
            while len(frames) < self.max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Sample frame
                if frame_count % sample_rate == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                
                frame_count += 1
                
                # Stop if reached duration limit
                if frame_count >= total_frames:
                    break
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from video")
            
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            raise
    
    def _download_video(self, video_url: str) -> str:
        """Download video from URL to temporary file"""
        import requests
        from tempfile import NamedTemporaryFile
        
        try:
            logger.info(f"Downloading video from {video_url}")
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = NamedTemporaryFile(delete=False, suffix='.mp4')
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.close()
            
            logger.info(f"Video downloaded to {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            raise
    
    def _save_temp_frame(self, frame: np.ndarray, index: int) -> str:
        """Save frame to temporary file"""
        from tempfile import gettempdir
        
        temp_dir = Path(gettempdir()) / "citypulse_frames"
        temp_dir.mkdir(exist_ok=True)
        
        temp_path = temp_dir / f"frame_{index}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
        
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(temp_path), frame_bgr)
        
        return str(temp_path)
    
    def _aggregate_results(
        self,
        frame_results: List[VisionAnalysisResponse]
    ) -> VisionAnalysisResponse:
        """
        Aggregate results from multiple frames into single response
        
        Args:
            frame_results: List of VisionAnalysisResponse from each frame
        
        Returns:
            Aggregated VisionAnalysisResponse
        """
        if not frame_results:
            raise ValueError("No frame results to aggregate")
        
        # Vote for event type (most common)
        event_type_votes = {}
        for result in frame_results:
            event_type = result.event_type
            event_type_votes[event_type] = event_type_votes.get(event_type, 0) + 1
        
        most_common_event = max(event_type_votes, key=event_type_votes.get)
        
        # Vote for severity (highest)
        from utils.schemas import SeverityLevel
        severity_order = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        max_severity = max([result.severity for result in frame_results], 
                          key=lambda s: severity_order.index(s))
        
        # Average confidence
        avg_confidence = sum(r.confidence for r in frame_results) / len(frame_results)
        
        # Merge detected objects (unique by class_name)
        all_objects = {}
        for result in frame_results:
            for obj in result.detected_objects:
                if obj.class_name not in all_objects or obj.confidence > all_objects[obj.class_name].confidence:
                    all_objects[obj.class_name] = obj
        
        merged_objects = list(all_objects.values())
        
        # Merge tags (unique)
        all_tags = set()
        for result in frame_results:
            all_tags.update(result.tags)
        
        # Generate enhanced description
        description = self._generate_video_description(
            most_common_event,
            merged_objects,
            len(frame_results)
        )
        
        return VisionAnalysisResponse(
            event_type=most_common_event,
            description=description,
            confidence=avg_confidence,
            severity=max_severity,
            detected_objects=merged_objects,
            tags=sorted(list(all_tags)),
            processing_time_ms=0.0,  # Will be updated by caller
            model_version=f"yolov8{config.vision.yolo_model_size}_video"
        )
    
    def _generate_video_description(
        self,
        event_type,
        detected_objects: List[DetectedObject],
        num_frames: int
    ) -> str:
        """Generate description for video analysis"""
        obj_summary = ", ".join([obj.class_name for obj in detected_objects[:5]])
        
        base_descriptions = {
            "traffic": f"Traffic situation observed across {num_frames} frames",
            "obstruction": f"Road obstruction detected consistently in video",
            "flooding": f"Flooding visible throughout video footage",
            "fire": f"Fire or smoke detected - emergency situation",
            "protest": f"Large gathering/crowd movement observed",
            "accident": f"Accident scene visible in video",
        }
        
        event_key = event_type.value if hasattr(event_type, 'value') else str(event_type)
        base = base_descriptions.get(event_key, f"Event detected in video: {event_type}")
        
        if detected_objects:
            return f"{base}. Objects detected: {obj_summary}"
        return base


if __name__ == "__main__":
    # Test video analyzer
    logger.info("Testing Video Analyzer...")
    
    analyzer = VideoAnalyzer()
    logger.info("Video analyzer initialized successfully")
    
    print("\n" + "="*60)
    print("✅ Video Analyzer Test Passed")
    print("="*60)
    print("\nTo test with an actual video:")
    print('  result = analyzer.analyze_video("path/to/video.mp4")')
    print('  print(result.model_dump_json(indent=2))')
