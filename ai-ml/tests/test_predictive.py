"""Test suite for predictive module"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch

from predictive.anomaly_detector import AnomalyDetector
from predictive.timeseries_model import TimeSeriesForecaster
from utils.schemas import SeverityLevel


@pytest.fixture
def anomaly_detector():
    """Fixture for anomaly detector"""
    return AnomalyDetector()


@pytest.fixture
def time_series_forecaster():
    """Fixture for time series forecaster"""
    return TimeSeriesForecaster()


@pytest.fixture
def sample_historical_data():
    """Create sample historical data"""
    dates = pd.date_range(start='2025-09-01', end='2025-10-01', freq='h')
    data = {
        'timestamp': dates,
        'event_type': ['traffic'] * len(dates),
        'location': ['MG Road'] * len(dates)
    }
    return pd.DataFrame(data)


class TestAnomalyDetector:
    """Test cases for AnomalyDetector"""
    
    def test_initialization(self, anomaly_detector):
        """Test detector initialization"""
        assert anomaly_detector is not None
        assert anomaly_detector.model is not None
        assert 0 < anomaly_detector.contamination < 1
    
    def test_detect_anomaly_no_events(self, anomaly_detector):
        """Test anomaly detection with no recent events"""
        result = anomaly_detector.detect_anomaly(
            event_type="traffic",
            location="test_location"
        )
        
        assert result is not None
        assert isinstance(result.is_anomaly, bool)
        assert 0 <= result.anomaly_score <= 1
        assert isinstance(result.severity, SeverityLevel)
    
    def test_calculate_severity(self, anomaly_detector):
        """Test severity calculation"""
        critical = anomaly_detector._calculate_severity(0.95, 25)
        assert critical == SeverityLevel.CRITICAL
        
        high = anomaly_detector._calculate_severity(0.80, 15)
        assert high == SeverityLevel.HIGH
        
        low = anomaly_detector._calculate_severity(0.3, 3)
        assert low == SeverityLevel.LOW
    
    def test_train_with_data(self, anomaly_detector, sample_historical_data):
        """Test training with sample data"""
        anomaly_detector.train(sample_historical_data)
        assert anomaly_detector.is_trained is True

    def test_prepare_features_does_not_mutate_input(self, anomaly_detector):
        data = pd.DataFrame({
            "timestamp": pd.date_range("2025-10-01", periods=2, freq="h"),
            "event_type": ["traffic", "traffic"],
            "location": ["MG Road", "MG Road"],
        })
        original_columns = data.columns.tolist()
        anomaly_detector._prepare_features(data)
        assert data.columns.tolist() == original_columns

    def test_below_minimum_reports_is_not_anomaly(self, anomaly_detector):
        with patch("predictive.anomaly_detector.firebase_client.get_recent_events", return_value=[]):
            result = anomaly_detector.detect_anomaly("traffic", "MG Road")
        assert result.is_anomaly is False
        assert result.severity == SeverityLevel.LOW

    def test_alert_message_and_type(self, anomaly_detector):
        anomaly = type("Result", (), {
            "is_anomaly": True, "event_count": 12
        })()
        message, alert_type = anomaly_detector.generate_alert_message(
            anomaly, "traffic", "MG Road"
        )
        assert "traffic surge" in message
        assert alert_type.value == "traffic_surge"

    def test_non_anomaly_has_no_alert(self, anomaly_detector):
        result = type("Result", (), {"is_anomaly": False})()
        assert anomaly_detector.generate_alert_message(result, "traffic") is None


class TestTimeSeriesForecaster:
    """Test cases for TimeSeriesForecaster"""
    
    def test_initialization(self, time_series_forecaster):
        """Test forecaster initialization"""
        assert time_series_forecaster is not None
        assert time_series_forecaster.forecast_periods > 0
    
    def test_prepare_prophet_data(self, time_series_forecaster, sample_historical_data):
        """Test data preparation for Prophet"""
        prophet_df = time_series_forecaster._prepare_prophet_data(sample_historical_data)
        
        assert 'ds' in prophet_df.columns
        assert 'y' in prophet_df.columns
        assert len(prophet_df) > 0
    
    @pytest.mark.skip(reason="Training requires sufficient historical data")
    def test_train_and_forecast(self, time_series_forecaster, sample_historical_data):
        """Test training and forecasting (requires more data)"""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
