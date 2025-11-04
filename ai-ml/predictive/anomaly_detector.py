"""
Anomaly Detection for City Events
Uses Isolation Forest and statistical methods to detect abnormal event patterns
"""

import time
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from utils.logger import get_logger
from utils.schemas import SeverityLevel, AnomalyResult, AlertType
from utils.firebase_client import firebase_client
from config.config import config

logger = get_logger("anomaly_detector")


class AnomalyDetector:
    """
    Anomaly detection for city events
    
    Features:
    - Isolation Forest for outlier detection
    - Statistical threshold analysis
    - Time-window based analysis
    - Alert generation for anomalies
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize anomaly detector
        
        Args:
            model_path: Path to saved model (creates new if None)
        """
        self.model_path = model_path or config.predictive.anomaly_model_path
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Configuration
        self.contamination = config.predictive.contamination
        self.n_estimators = config.predictive.n_estimators
        self.anomaly_threshold = config.predictive.anomaly_threshold
        self.min_reports = config.predictive.min_reports_for_anomaly
        self.time_window = config.predictive.prediction_window_minutes
        
        # Load or create model
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        model_path = Path(self.model_path)
        
        if model_path.exists():
            try:
                with open(model_path, 'rb') as f:
                    saved_data = pickle.load(f)
                    self.model = saved_data['model']
                    self.scaler = saved_data['scaler']
                    self.is_trained = saved_data.get('is_trained', False)
                
                logger.success(f"Loaded anomaly detection model from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, creating new one")
                self._create_new_model()
        else:
            self._create_new_model()
    
    def _create_new_model(self):
        """Create new Isolation Forest model"""
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        logger.info("Created new Isolation Forest model")
    
    def train(self, historical_data: Optional[pd.DataFrame] = None):
        """
        Train anomaly detection model on historical data
        
        Args:
            historical_data: DataFrame with historical events
                            If None, fetches from Firebase
        """
        try:
            logger.info("Training anomaly detection model...")
            
            # Get historical data if not provided
            if historical_data is None:
                historical_data = self._fetch_historical_data()
            
            if historical_data.empty:
                logger.warning("No historical data available for training")
                return
            
            # Prepare features
            features = self._prepare_features(historical_data)
            
            if len(features) < 50:
                logger.warning(f"Insufficient data for training: {len(features)} samples")
                return
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train model
            self.model.fit(features_scaled)
            self.is_trained = True
            
            # Save model
            self._save_model()
            
            logger.success(f"Model trained on {len(features)} samples")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def detect_anomaly(
        self,
        event_type: Optional[str] = None,
        location: Optional[str] = None,
        time_window_minutes: Optional[int] = None
    ) -> AnomalyResult:
        """
        Detect anomalies in recent events
        
        Args:
            event_type: Filter by event type
            location: Filter by location
            time_window_minutes: Time window for analysis
        
        Returns:
            AnomalyResult with detection details
        """
        start_time = time.time()
        
        try:
            # Get recent events
            time_window = time_window_minutes or self.time_window
            recent_events = firebase_client.get_recent_events(
                event_type=event_type,
                location=location,
                minutes=time_window
            )
            
            event_count = len(recent_events)
            logger.info(f"Analyzing {event_count} events in last {time_window} minutes")
            
            # Check minimum threshold
            if event_count < self.min_reports:
                return AnomalyResult(
                    is_anomaly=False,
                    anomaly_score=0.0,
                    event_count=event_count,
                    baseline_count=float(self.min_reports),
                    severity=SeverityLevel.LOW
                )
            
            # Method 1: Statistical analysis (always available)
            baseline_count = self._calculate_baseline(event_type, location)
            statistical_anomaly = event_count > (baseline_count * 2.5)
            
            # Method 2: ML-based detection (if trained)
            ml_anomaly_score = 0.0
            if self.is_trained and recent_events:
                ml_anomaly_score = self._ml_anomaly_detection(recent_events)
            
            # Combine methods
            is_anomaly = statistical_anomaly or ml_anomaly_score > self.anomaly_threshold
            
            # Calculate final anomaly score
            anomaly_score = max(
                min(event_count / max(baseline_count * 2, 1), 1.0),
                ml_anomaly_score
            )
            
            # Determine severity
            severity = self._calculate_severity(anomaly_score, event_count)
            
            logger.info(f"Anomaly detection: {'YES' if is_anomaly else 'NO'} (score: {anomaly_score:.2f})")
            
            return AnomalyResult(
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                event_count=event_count,
                baseline_count=baseline_count,
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            raise
    
    def _fetch_historical_data(self, days: int = 30) -> pd.DataFrame:
        """Fetch historical data from Firebase"""
        try:
            events = firebase_client.get_historical_data(days=days)
            
            if not events:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(events)
            
            # Ensure required columns
            required_cols = ['timestamp', 'event_type', 'location']
            if not all(col in df.columns for col in required_cols):
                logger.warning("Missing required columns in historical data")
                return pd.DataFrame()
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return pd.DataFrame()
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for anomaly detection
        
        Features:
        - Events per hour
        - Events per location
        - Time of day
        - Day of week
        """
        # Aggregate by hour and location
        data['hour'] = data['timestamp'].dt.floor('H')
        data['hour_of_day'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        
        # Count events per hour-location
        aggregated = data.groupby(['hour', 'location']).agg({
            'event_type': 'count',
            'hour_of_day': 'first',
            'day_of_week': 'first'
        }).reset_index()
        
        aggregated.columns = ['hour', 'location', 'event_count', 'hour_of_day', 'day_of_week']
        
        # Encode location (use top N locations, others as 'other')
        top_locations = data['location'].value_counts().head(20).index
        aggregated['location_encoded'] = aggregated['location'].apply(
            lambda x: list(top_locations).index(x) if x in top_locations else 20
        )
        
        # Select features
        features = aggregated[['event_count', 'hour_of_day', 'day_of_week', 'location_encoded']].values
        
        return features
    
    def _ml_anomaly_detection(self, events: List[Dict]) -> float:
        """Use ML model to detect anomalies"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(events)
            
            # Prepare single sample
            current_features = self._prepare_features(df)
            
            if len(current_features) == 0:
                return 0.0
            
            # Take mean of features (aggregate to single sample)
            sample = current_features.mean(axis=0).reshape(1, -1)
            
            # Scale
            sample_scaled = self.scaler.transform(sample)
            
            # Predict (-1 for anomaly, 1 for normal)
            prediction = self.model.predict(sample_scaled)[0]
            
            # Get anomaly score (lower score = more anomalous)
            score = self.model.score_samples(sample_scaled)[0]
            
            # Convert to 0-1 scale (higher = more anomalous)
            anomaly_score = 1.0 - (score + 0.5)  # Normalize roughly to 0-1
            anomaly_score = np.clip(anomaly_score, 0, 1)
            
            return float(anomaly_score)
            
        except Exception as e:
            logger.warning(f"ML anomaly detection failed: {e}")
            return 0.0
    
    def _calculate_baseline(
        self,
        event_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> float:
        """Calculate baseline event count"""
        try:
            # Get historical average for same time window
            historical = firebase_client.get_historical_data(
                event_type=event_type,
                days=7
            )
            
            if not historical:
                return float(self.min_reports)
            
            # Filter by location if provided
            if location:
                historical = [e for e in historical if e.get('location') == location]
            
            # Calculate hourly average
            total_hours = 7 * 24
            baseline = len(historical) / total_hours * (self.time_window / 60)
            
            return max(baseline, 1.0)
            
        except Exception as e:
            logger.warning(f"Baseline calculation failed: {e}")
            return float(self.min_reports)
    
    def _calculate_severity(self, anomaly_score: float, event_count: int) -> SeverityLevel:
        """Calculate severity level based on anomaly score and count"""
        if anomaly_score >= 0.9 or event_count > 20:
            return SeverityLevel.CRITICAL
        elif anomaly_score >= 0.75 or event_count > 10:
            return SeverityLevel.HIGH
        elif anomaly_score >= 0.6 or event_count > 5:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _save_model(self):
        """Save model to disk"""
        try:
            model_path = Path(self.model_path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'is_trained': self.is_trained,
                    'config': {
                        'contamination': self.contamination,
                        'n_estimators': self.n_estimators
                    }
                }, f)
            
            logger.success(f"Model saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def generate_alert_message(
        self,
        anomaly_result: AnomalyResult,
        event_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> Tuple[str, AlertType]:
        """
        Generate alert message from anomaly result
        
        Returns:
            Tuple of (alert_message, alert_type)
        """
        if not anomaly_result.is_anomaly:
            return "", None
        
        # Determine alert type
        alert_type_map = {
            "traffic": AlertType.TRAFFIC_SURGE,
            "power_outage": AlertType.POWER_GRID_ISSUE,
            "flooding": AlertType.FLOODING_RISK,
            "accident": AlertType.ACCIDENT_CLUSTER,
        }
        
        alert_type = alert_type_map.get(event_type, AlertType.ANOMALY)
        
        # Generate message
        location_str = f" in {location}" if location else ""
        event_str = f"{event_type} " if event_type else ""
        
        messages = {
            AlertType.TRAFFIC_SURGE: f"Unusual traffic surge{location_str} - {anomaly_result.event_count} reports in {self.time_window} minutes",
            AlertType.POWER_GRID_ISSUE: f"Possible grid outage{location_str} - {anomaly_result.event_count} power outage reports",
            AlertType.FLOODING_RISK: f"Flooding risk{location_str} - multiple reports detected",
            AlertType.ACCIDENT_CLUSTER: f"Accident cluster{location_str} - {anomaly_result.event_count} incidents reported",
            AlertType.ANOMALY: f"Abnormal {event_str}activity{location_str} - {anomaly_result.event_count} events detected"
        }
        
        alert_message = messages.get(alert_type, f"Anomaly detected{location_str}")
        
        return alert_message, alert_type


if __name__ == "__main__":
    # Test anomaly detector
    logger.info("Testing Anomaly Detector...")
    
    detector = AnomalyDetector()
    logger.info("Anomaly detector initialized successfully")
    
    # Test detection with mock data
    result = detector.detect_anomaly(
        event_type="traffic",
        location="MG Road"
    )
    
    print("\n" + "="*60)
    print("✅ Anomaly Detector Test Passed")
    print("="*60)
    print(f"\nTest Result:")
    print(f"  Is Anomaly: {result.is_anomaly}")
    print(f"  Score: {result.anomaly_score:.2f}")
    print(f"  Event Count: {result.event_count}")
    print(f"  Severity: {result.severity.value}")
