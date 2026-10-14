"""Offline regression tests for vision and forecast hardening."""
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from predictive.timeseries_model import TimeSeriesForecaster
from utils.schemas import DetectedObject, EventType, SeverityLevel
from vision.image_classifier import ImageClassifier


def test_person_alone_is_not_a_protest():
    classifier = object.__new__(ImageClassifier)
    classifier.event_mappings = {
        "person": {"event_type": EventType.PROTEST, "severity": SeverityLevel.MEDIUM}
    }
    objects = [DetectedObject(class_name="person", confidence=0.9, bbox=[0, 0, 1, 1])]
    assert classifier._classify_event(objects) == (EventType.OTHER, SeverityLevel.LOW)


def test_custom_only_mapping_is_gated():
    classifier = object.__new__(ImageClassifier)
    classifier.event_mappings = {
        "pothole": {"event_type": EventType.CIVIC_ISSUE, "severity": SeverityLevel.MEDIUM}
    }
    classifier.model = Mock(names={0: "car"})
    classifier._gate_mappings_to_model()
    assert classifier.event_mappings["pothole"]["requires_custom_weights"] is True


@pytest.mark.parametrize("url", ["file:///tmp/image.jpg", "http://127.0.0.1/image.jpg"])
def test_remote_image_url_safety(url):
    classifier = object.__new__(ImageClassifier)
    with pytest.raises(ValueError):
        classifier._load_image(url)


def test_forecast_without_model_is_empty():
    forecaster = object.__new__(TimeSeriesForecaster)
    forecaster.models = {}
    forecaster.forecast_periods = 24
    with patch.object(forecaster, "_load_model"), patch.object(
        forecaster, "train", return_value=False
    ):
        assert forecaster.forecast("traffic", periods=2) == []


def test_forecast_errors_are_not_silenced():
    forecaster = object.__new__(TimeSeriesForecaster)
    forecaster.models = {"traffic": Mock()}
    forecaster.forecast_periods = 24
    forecaster.models["traffic"].make_future_dataframe.side_effect = RuntimeError("boom")
    with pytest.raises(RuntimeError, match="boom"):
        forecaster.forecast("traffic", periods=2)
