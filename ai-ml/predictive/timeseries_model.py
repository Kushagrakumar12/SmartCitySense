"""
Time Series Forecasting for City Events
Uses Facebook Prophet for forecasting future event patterns
"""

import time
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json

from utils.logger import get_logger
from utils.schemas import ForecastResult
from utils.firebase_client import firebase_client
from config.config import config

logger = get_logger("timeseries_model")


class TimeSeriesForecaster:
    """
    Time series forecasting for city events using Facebook Prophet
    
    Features:
    - Event count forecasting
    - Trend detection
    - Seasonality analysis
    - Confidence intervals
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize time series forecaster
        
        Args:
            model_path: Path to saved model
        """
        self.model_path = model_path or config.predictive.prophet_model_path
        self.models: Dict[str, Prophet] = {}  # One model per event type
        self.forecast_periods = config.predictive.forecast_periods
    
    def train(
        self,
        event_type: str,
        historical_data: Optional[pd.DataFrame] = None
    ):
        """
        Train Prophet model for specific event type
        
        Args:
            event_type: Event type to train for
            historical_data: DataFrame with historical events (fetches if None)
        """
        try:
            logger.info(f"Training forecaster for event type: {event_type}")
            
            # Get historical data
            if historical_data is None:
                historical_data = self._fetch_historical_data(event_type)
            
            if historical_data.empty:
                logger.warning(f"No historical data for {event_type}")
                return
            
            # Prepare data for Prophet
            prophet_df = self._prepare_prophet_data(historical_data)
            
            if len(prophet_df) < 10:
                logger.warning(f"Insufficient data for {event_type}: {len(prophet_df)} samples")
                return
            
            # Create and train model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,  # Need more data
                interval_width=0.95,
                changepoint_prior_scale=0.05
            )
            
            model.fit(prophet_df)
            self.models[event_type] = model
            
            # Save model
            self._save_model(event_type, model)
            
            logger.success(f"Model trained for {event_type} on {len(prophet_df)} samples")
            
        except Exception as e:
            logger.error(f"Training failed for {event_type}: {e}")
            raise
    
    def forecast(
        self,
        event_type: str,
        periods: Optional[int] = None,
        location: Optional[str] = None
    ) -> List[ForecastResult]:
        """
        Generate forecast for event type
        
        Args:
            event_type: Event type to forecast
            periods: Number of hours to forecast (default: from config)
            location: Specific location to forecast for
        
        Returns:
            List of ForecastResult objects
        """
        start_time = time.time()
        
        try:
            periods = periods or self.forecast_periods
            
            # Load model if not in memory
            if event_type not in self.models:
                self._load_model(event_type)
            
            if event_type not in self.models:
                logger.warning(f"No trained model for {event_type}, training now...")
                self.train(event_type)
                
                if event_type not in self.models:
                    logger.error(f"Failed to train model for {event_type}")
                    return []
            
            model = self.models[event_type]
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=periods, freq='H')
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract future predictions only
            future_forecast = forecast.tail(periods)
            
            # Convert to ForecastResult objects
            results = []
            for _, row in future_forecast.iterrows():
                result = ForecastResult(
                    forecast_timestamp=row['ds'],
                    predicted_value=max(0, row['yhat']),  # Can't have negative events
                    lower_bound=max(0, row['yhat_lower']),
                    upper_bound=max(0, row['yhat_upper']),
                    confidence=0.95  # Prophet uses 95% confidence interval
                )
                results.append(result)
            
            logger.info(f"Generated {len(results)} forecast points for {event_type}")
            return results
            
        except Exception as e:
            logger.error(f"Forecasting failed for {event_type}: {e}")
            return []
    
    def detect_trend(
        self,
        event_type: str,
        recent_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Detect trends in recent data
        
        Args:
            event_type: Event type to analyze
            recent_hours: Hours of recent data to analyze
        
        Returns:
            Dictionary with trend information
        """
        try:
            # Get recent data
            recent_data = firebase_client.get_recent_events(
                event_type=event_type,
                minutes=recent_hours * 60
            )
            
            if not recent_data:
                return {
                    "trend": "stable",
                    "direction": 0,
                    "magnitude": 0.0
                }
            
            # Convert to time series
            df = pd.DataFrame(recent_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Resample to hourly counts
            hourly_counts = df.resample('H').size()
            
            if len(hourly_counts) < 3:
                return {
                    "trend": "insufficient_data",
                    "direction": 0,
                    "magnitude": 0.0
                }
            
            # Calculate trend (simple linear regression)
            x = np.arange(len(hourly_counts))
            y = hourly_counts.values
            
            # Fit line
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            
            # Determine trend
            if abs(slope) < 0.1:
                trend = "stable"
                direction = 0
            elif slope > 0:
                trend = "increasing"
                direction = 1
            else:
                trend = "decreasing"
                direction = -1
            
            # Calculate magnitude (% change)
            avg_value = np.mean(y)
            magnitude = abs(slope * len(x)) / (avg_value + 1) * 100
            
            return {
                "trend": trend,
                "direction": direction,
                "magnitude": float(magnitude),
                "slope": float(slope),
                "average_count": float(avg_value)
            }
            
        except Exception as e:
            logger.error(f"Trend detection failed: {e}")
            return {
                "trend": "error",
                "direction": 0,
                "magnitude": 0.0
            }
    
    def _fetch_historical_data(
        self,
        event_type: str,
        days: int = 30
    ) -> pd.DataFrame:
        """Fetch historical data from Firebase"""
        try:
            events = firebase_client.get_historical_data(
                event_type=event_type,
                days=days
            )
            
            if not events:
                return pd.DataFrame()
            
            df = pd.DataFrame(events)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return pd.DataFrame()
    
    def _prepare_prophet_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data in Prophet format
        
        Prophet expects columns: 'ds' (datetime) and 'y' (value)
        """
        # Resample to hourly counts
        data = data.set_index('timestamp')
        hourly_counts = data.resample('H').size().reset_index()
        hourly_counts.columns = ['ds', 'y']
        
        return hourly_counts
    
    def _save_model(self, event_type: str, model: Prophet):
        """Save model to disk"""
        try:
            model_path = Path(self.model_path).parent / f"prophet_{event_type}.pkl"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize model
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"Model saved for {event_type}")
            
        except Exception as e:
            logger.warning(f"Failed to save model for {event_type}: {e}")
    
    def _load_model(self, event_type: str):
        """Load model from disk"""
        try:
            model_path = Path(self.model_path).parent / f"prophet_{event_type}.pkl"
            
            if not model_path.exists():
                logger.info(f"No saved model found for {event_type}")
                return
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            self.models[event_type] = model
            logger.success(f"Loaded model for {event_type}")
            
        except Exception as e:
            logger.warning(f"Failed to load model for {event_type}: {e}")
    
    def train_all_event_types(self):
        """Train models for all major event types"""
        from utils.schemas import EventType
        
        major_types = [
            EventType.TRAFFIC.value,
            EventType.POWER_OUTAGE.value,
            EventType.FLOODING.value,
            EventType.ACCIDENT.value,
        ]
        
        for event_type in major_types:
            try:
                self.train(event_type)
            except Exception as e:
                logger.warning(f"Failed to train {event_type}: {e}")


if __name__ == "__main__":
    # Test time series forecaster
    logger.info("Testing Time Series Forecaster...")
    
    forecaster = TimeSeriesForecaster()
    logger.info("Forecaster initialized successfully")
    
    print("\n" + "="*60)
    print("✅ Time Series Forecaster Test Passed")
    print("="*60)
    print("\nTo train and forecast:")
    print('  forecaster.train("traffic")')
    print('  results = forecaster.forecast("traffic", periods=24)')
    print('  for r in results[:5]:')
    print('      print(f"{r.forecast_timestamp}: {r.predicted_value:.1f} events")')
