"""Test suite for vision module"""
import pytest
from pathlib import Path
import numpy as np
import cv2

from vision.image_classifier import ImageClassifier
from vision.video_analyzer import VideoAnalyzer
from utils.schemas import EventType, SeverityLevel


@pytest.fixture
def image_classifier():
    """Fixture for image classifier"""
    return ImageClassifier()


@pytest.fixture
def video_analyzer():
    """Fixture for video analyzer"""
    return VideoAnalyzer()


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image"""
    image = np.zeros((640, 640, 3), dtype=np.uint8)
    # Draw some simple shapes
    cv2.rectangle(image, (100, 100), (500, 500), (255, 0, 0), -1)
    
    image_path = tmp_path / "test_image.jpg"
    cv2.imwrite(str(image_path), image)
    return str(image_path)


class TestImageClassifier:
    """Test cases for ImageClassifier"""
    
    def test_initialization(self, image_classifier):
        """Test classifier initialization"""
        assert image_classifier is not None
        assert image_classifier.model is not None
        assert image_classifier.device in ['cuda', 'cpu']
    
    def test_event_mappings(self, image_classifier):
        """Test event mappings exist"""
        assert len(image_classifier.event_mappings) > 0
        assert 'car' in image_classifier.event_mappings
        assert 'tree' in image_classifier.event_mappings
    
    def test_classify_image(self, image_classifier, sample_image):
        """Test image classification"""
        result = image_classifier.classify_image(sample_image)
        
        assert result is not None
        assert isinstance(result.event_type, EventType)
        assert isinstance(result.severity, SeverityLevel)
        assert 0 <= result.confidence <= 1
        assert result.processing_time_ms > 0
        assert isinstance(result.description, str)
        assert isinstance(result.tags, list)


class TestVideoAnalyzer:
    """Test cases for VideoAnalyzer"""
    
    def test_initialization(self, video_analyzer):
        """Test video analyzer initialization"""
        assert video_analyzer is not None
        assert video_analyzer.classifier is not None
    
    @pytest.mark.skip(reason="Requires sample video file")
    def test_analyze_video(self, video_analyzer):
        """Test video analysis (requires video file)"""
        # This would need an actual video file to test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
