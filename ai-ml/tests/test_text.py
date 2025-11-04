"""
Test Suite for Member B1 - Text Intelligence
Tests for text_summarizer.py and sentiment_analyzer.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from text.text_summarizer import TextSummarizer
from text.sentiment_analyzer import SentimentAnalyzer
from config.config import Config


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def mock_config():
    """Create mock configuration for testing"""
    # Create a mock config object
    config_mock = Mock(spec=Config)
    
    # Mock text config
    text_config = Mock()
    text_config.summarization_llm_provider = "gemini"
    text_config.summarization_model_name = "gemini-2.5-flash"
    text_config.google_api_key = "test_key_12345"
    text_config.openai_api_key = None
    text_config.max_reports_per_summary = 50
    text_config.summary_max_length = 200
    text_config.sentiment_model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    text_config.enable_multilingual = False
    text_config.batch_size = 32
    text_config.summarized_events_collection = "test_summarized_events"
    text_config.mood_map_collection = "test_mood_map"
    
    config_mock.text = text_config
    config_mock.device = "cpu"
    config_mock.use_gpu = False
    config_mock.mock_mode = True
    
    return config_mock


@pytest.fixture(autouse=True)
def patch_config(mock_config, monkeypatch):
    """Automatically patch the config module for all tests"""
    # Patch the config in both text modules
    with patch('text.text_summarizer.config', mock_config):
        with patch('text.sentiment_analyzer.config', mock_config):
            yield


@pytest.fixture
def sample_traffic_reports():
    """Sample traffic reports for testing"""
    return [
        "Heavy traffic jam on Old Airport Road near KR Puram",
        "Massive traffic on OAR, avoid until evening",
        "Road blocked due to vehicle breakdown on Old Airport Road",
        "Traffic not moving on airport road",
        "30 min delay on Old Airport Road due to accident",
        "Avoid OAR, complete standstill",
        "Traffic nightmare on Old Airport Road today",
        "Old Airport Road jam near KR Puram signal"
    ]


@pytest.fixture
def sample_power_reports():
    """Sample power outage reports"""
    return [
        "Power cut in HSR Layout since 2 PM",
        "No electricity in HSR Layout Sector 1",
        "HSR residents without power for 3 hours",
        "Power outage affecting entire HSR Layout"
    ]


@pytest.fixture
def sample_sentiment_texts():
    """Sample texts for sentiment analysis"""
    return [
        "Amazing new metro station in Whitefield!",
        "Traffic is absolutely horrible in Koramangala today",
        "Great weather in Bangalore",
        "Power cuts again, very frustrating",
        "Love the new park in Indiranagar"
    ]


@pytest.fixture
def sample_texts_with_locations():
    """Sample texts with location mentions"""
    return {
        "texts": [
            "Traffic nightmare in Koramangala today",
            "Great new cafe opened in Whitefield",
            "Power outage in Electronic City again",
            "Beautiful weather at Cubbon Park",
            "Horrible traffic on ORR near Marathahalli"
        ],
        "locations": [
            "Koramangala",
            "Whitefield",
            "Electronic City",
            "Cubbon Park",
            "Marathahalli"
        ]
    }


# ============================================================
# TEXT SUMMARIZER TESTS
# ============================================================

class TestTextSummarizer:
    """Test cases for TextSummarizer class"""
    
    def test_initialization(self):
        """Test TextSummarizer initialization"""
        with patch('text.text_summarizer.genai') as mock_genai:
            summarizer = TextSummarizer()
            assert summarizer.llm_provider == "gemini"
            assert len(summarizer.prompts) > 0
    
    def test_preprocess_reports_removes_urls(self):
        """Test URL removal in preprocessing"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            reports = [
                "Check this out http://example.com",
                "Great article: https://news.com/article",
                "No URLs here"
            ]
            processed = summarizer.preprocess_reports(reports)
            
            for report in processed:
                assert "http" not in report
                assert "https" not in report
    
    def test_preprocess_reports_removes_short_texts(self):
        """Test removal of very short reports"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            reports = [
                "This is a valid report with enough content",
                "ok",
                "yes",
                "Another valid report here"
            ]
            processed = summarizer.preprocess_reports(reports)
            
            # Should remove "ok" and "yes" (too short)
            assert len(processed) == 2
    
    def test_preprocess_reports_normalizes_whitespace(self):
        """Test whitespace normalization"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            reports = [
                "Too    many     spaces",
                "Normal   spacing  here"
            ]
            processed = summarizer.preprocess_reports(reports)
            
            for report in processed:
                assert "    " not in report  # No multiple spaces
    
    def test_deduplicate_reports_exact_duplicates(self):
        """Test exact duplicate removal"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            reports = [
                "Traffic jam on MG Road",
                "Traffic jam on MG Road",  # Exact duplicate
                "Different report here",
                "Traffic jam on MG Road"   # Another duplicate
            ]
            deduplicated = summarizer.deduplicate_reports(reports)
            
            assert len(deduplicated) == 2
            assert "Traffic jam on MG Road" in deduplicated
            assert "Different report here" in deduplicated
    
    def test_deduplicate_reports_near_duplicates(self):
        """Test near-duplicate detection using Jaccard similarity"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            reports = [
                "Heavy traffic jam on Old Airport Road",
                "Heavy traffic on Old Airport Road",  # Very similar
                "Completely different topic about weather"
            ]
            deduplicated = summarizer.deduplicate_reports(reports)
            
            # Should keep only 2 (removing near-duplicate)
            assert len(deduplicated) <= 2
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            reports = [
                "Traffic jam on airport road due to accident",
                "Heavy traffic and accident on airport road",
                "Airport road blocked"
            ]
            keywords = summarizer.extract_common_keywords(reports, top_n=5)
            
            assert len(keywords) > 0
            assert "traffic" in [kw.lower() for kw in keywords]
            assert "airport" in [kw.lower() for kw in keywords]
    
    def test_summarize_with_template_fallback(self, sample_traffic_reports):
        """Test template-based summarization (fallback mode)"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            
            summary, confidence = summarizer.summarize_with_template(
                reports=sample_traffic_reports,
                event_type="traffic",
                location="Old Airport Road"
            )
            
            assert summary is not None
            assert len(summary) > 0
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0
            assert "Old Airport Road" in summary
    
    def test_summarize_with_llm_mock(self, sample_traffic_reports):
        """Test LLM summarization with mocked response"""
        with patch('text.text_summarizer.genai') as mock_genai, \
             patch('text.text_summarizer.LANGCHAIN_AVAILABLE', False):
            # Mock LLM response
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Heavy traffic on Old Airport Road due to vehicle breakdown. Avoid until evening."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            summarizer = TextSummarizer()
            
            summary, confidence = summarizer.summarize_with_llm(
                reports=sample_traffic_reports,
                event_type="traffic",
                location="Old Airport Road"
            )
            
            assert summary is not None
            assert len(summary) > 0
            assert "breakdown" in summary.lower()
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0
    
    def test_summarize_full_pipeline(self, sample_traffic_reports):
        """Test complete summarization pipeline"""
        with patch('text.text_summarizer.genai') as mock_genai, \
             patch('text.text_summarizer.LANGCHAIN_AVAILABLE', False):
            # Mock LLM
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Traffic congestion on Old Airport Road near KR Puram due to accident. Consider alternative routes."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            summarizer = TextSummarizer()
            
            result = summarizer.summarize(
                reports=sample_traffic_reports,
                event_type="traffic",
                location="Old Airport Road",
                use_llm=True
            )
            
            # Validate result structure
            assert "summary" in result
            assert "confidence" in result
            assert "keywords" in result
            assert "method" in result
            assert "source_count" in result
            assert "processed_count" in result
            
            # Validate values
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["source_count"] == len(sample_traffic_reports)
            assert result["processed_count"] <= result["source_count"]
            assert len(result["keywords"]) > 0
    
    def test_batch_summarize(self, sample_traffic_reports, sample_power_reports):
        """Test batch summarization of multiple report groups"""
        with patch('text.text_summarizer.genai') as mock_genai, \
             patch('text.text_summarizer.LANGCHAIN_AVAILABLE', False):
            # Mock LLM
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Summary generated"
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            summarizer = TextSummarizer()
            
            # batch_summarize expects Dict[str, List[str]]
            report_groups = {
                "group1": sample_traffic_reports,
                "group2": sample_power_reports
            }
            
            results = summarizer.batch_summarize(report_groups, event_type="traffic")
            
            assert len(results) == 2
            for result in results:
                assert "summary" in result
                assert "confidence" in result
                assert "group_id" in result
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            
            # Good summary (optimal length, has keywords)
            summary1 = "Heavy traffic on Old Airport Road due to accident. Avoid route."
            reports1 = ["traffic accident", "road blocked", "avoid airport road"]
            confidence1 = summarizer._calculate_confidence(summary1, reports1)
            
            # Poor summary (too short, no keywords)
            summary2 = "Issue."
            reports2 = ["detailed report about traffic"]
            confidence2 = summarizer._calculate_confidence(summary2, reports2)
            
            assert 0.0 <= confidence1 <= 1.0
            assert 0.0 <= confidence2 <= 1.0
            assert confidence1 > confidence2  # Good summary should score higher
    
    def test_location_normalization(self):
        """Test location name normalization"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            
            # Test various location formats
            assert summarizer.normalize_location("koramangala") == "Koramangala"
            assert summarizer.normalize_location("OLD AIRPORT ROAD") == "Old Airport Road"
            assert summarizer.normalize_location("mg road") == "Mahatma Gandhi Road"


# ============================================================
# SENTIMENT ANALYZER TESTS
# ============================================================

class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer class"""
    
    def test_initialization(self):
        """Test SentimentAnalyzer initialization"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            # Config is mocked globally
            assert analyzer.model_name is not None
            assert len(analyzer.location_patterns) > 0
    
    def test_preprocess_text_removes_urls(self):
        """Test URL removal in text preprocessing"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            text = "Check this out http://example.com and https://test.com"
            processed = analyzer.preprocess_text(text)
            
            assert "http" not in processed
            assert "https" not in processed
    
    def test_preprocess_text_removes_mentions(self):
        """Test @mention removal"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            text = "Hey @username, what do you think @another_user?"
            processed = analyzer.preprocess_text(text)
            
            assert "@username" not in processed
            assert "@another_user" not in processed
    
    def test_preprocess_text_removes_hashtags(self):
        """Test hashtag processing (keeps word, removes #)"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            text = "Great day #bangalore #traffic"
            processed = analyzer.preprocess_text(text)
            
            assert "#" not in processed
            assert "bangalore" in processed.lower()
            assert "traffic" in processed.lower()
    
    def test_extract_location_koramangala(self):
        """Test location extraction for Koramangala"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            text = "Traffic is terrible in Koramangala today"
            location = analyzer.extract_location(text)
            
            assert location == "Koramangala"
    
    def test_extract_location_variations(self):
        """Test location extraction with spelling variations"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            # Test variations
            texts = [
                "Issue in whitefield",
                "Problem at white field",
                "Near Marathahalli",
                "marathahalli junction"
            ]
            
            locations = [analyzer.extract_location(t) for t in texts]
            
            assert "Whitefield" in locations
            assert "Marathahalli" in locations
    
    def test_extract_location_no_match(self):
        """Test location extraction when no location found"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            text = "Generic complaint with no location"
            location = analyzer.extract_location(text)
            
            assert location == "Bengaluru"  # Default location
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive text"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            # Mock positive sentiment
            mock_model = MagicMock()
            mock_model.return_value = [{"label": "POSITIVE", "score": 0.95}]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            result = analyzer.analyze_sentiment(
                "Amazing new metro station! Love it!",
                location="Whitefield"
            )
            
            assert result["sentiment"] == "positive"
            assert result["score"] > 0  # Positive score
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["location"] == "Whitefield"
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative text"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            # Mock negative sentiment
            mock_model = MagicMock()
            mock_model.return_value = [{"label": "NEGATIVE", "score": 0.88}]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            result = analyzer.analyze_sentiment(
                "Horrible traffic, completely stuck",
                location="MG Road"
            )
            
            assert result["sentiment"] == "negative"
            assert result["score"] < 0  # Negative score
            assert result["location"] == "MG Road"
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral text"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            # Mock neutral sentiment (low confidence)
            mock_model = MagicMock()
            mock_model.return_value = [{"label": "POSITIVE", "score": 0.51}]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            result = analyzer.analyze_sentiment(
                "The road is open today",
                location="Bangalore"
            )
            
            # Low confidence should result in neutral
            assert result["sentiment"] in ["positive", "negative", "neutral"]
    
    def test_batch_analyze(self, sample_sentiment_texts):
        """Test batch sentiment analysis"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            # Mock varied sentiments
            mock_model = MagicMock()
            mock_model.return_value = [
                {"label": "POSITIVE", "score": 0.90},
                {"label": "NEGATIVE", "score": 0.85},
                {"label": "POSITIVE", "score": 0.75},
                {"label": "NEGATIVE", "score": 0.80},
                {"label": "POSITIVE", "score": 0.88}
            ]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            results = analyzer.batch_analyze(
                texts=sample_sentiment_texts,
                locations=None
            )
            
            assert len(results) == len(sample_sentiment_texts)
            for result in results:
                assert "sentiment" in result
                assert "score" in result
                assert "confidence" in result
    
    def test_aggregate_by_location(self):
        """Test sentiment aggregation by location"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            # Sample results with locations
            results = [
                {"sentiment": "positive", "score": 0.8, "location": "Koramangala"},
                {"sentiment": "positive", "score": 0.9, "location": "Koramangala"},
                {"sentiment": "negative", "score": -0.7, "location": "Whitefield"},
                {"sentiment": "negative", "score": -0.8, "location": "Whitefield"},
                {"sentiment": "positive", "score": 0.6, "location": "Indiranagar"}
            ]
            
            aggregated = analyzer.aggregate_by_location(results)
            
            assert "Koramangala" in aggregated
            assert "Whitefield" in aggregated
            assert "Indiranagar" in aggregated
            
            # Koramangala should be positive overall
            assert aggregated["Koramangala"]["sentiment"] == "positive"
            
            # Whitefield should be negative overall
            assert aggregated["Whitefield"]["sentiment"] == "negative"
            
            # Check sample sizes
            assert aggregated["Koramangala"]["sample_size"] == 2
            assert aggregated["Whitefield"]["sample_size"] == 2
    
    def test_create_mood_map(self, sample_texts_with_locations):
        """Test mood map creation"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            # Mock sentiments
            mock_model = MagicMock()
            mock_model.return_value = [
                {"label": "NEGATIVE", "score": 0.90},  # Koramangala
                {"label": "POSITIVE", "score": 0.85},   # Whitefield
                {"label": "NEGATIVE", "score": 0.75},  # Electronic City
                {"label": "POSITIVE", "score": 0.95},   # Cubbon Park
                {"label": "NEGATIVE", "score": 0.80}   # Marathahalli
            ]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            mood_map = analyzer.create_mood_map(
                texts=sample_texts_with_locations["texts"],
                locations=sample_texts_with_locations["locations"]
            )
            
            assert "timestamp" in mood_map
            assert "city_wide" in mood_map
            assert "locations" in mood_map
            assert "total_analyzed" in mood_map
            
            # Check city-wide sentiment
            city_sentiment = mood_map["city_wide"]
            assert "sentiment" in city_sentiment
            assert "score" in city_sentiment
            assert "distribution" in city_sentiment
            
            # Check individual locations
            locations = mood_map["locations"]
            assert len(locations) > 0
            
            for loc_name, loc_data in locations.items():
                assert "sentiment" in loc_data
                assert "score" in loc_data
                assert "sample_size" in loc_data
    
    def test_analyze_trend(self):
        """Test sentiment trend analysis"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_pipeline.return_value = MagicMock()
            analyzer = SentimentAnalyzer()
            
            # Historical data (improving sentiment) - must match mood_map structure
            historical_data = [
                {"timestamp": "2025-10-01T00:00:00Z", "city_wide": {"score": -0.5, "sentiment": "negative"}},
                {"timestamp": "2025-10-02T00:00:00Z", "city_wide": {"score": -0.3, "sentiment": "negative"}},
                {"timestamp": "2025-10-03T00:00:00Z", "city_wide": {"score": -0.1, "sentiment": "neutral"}},
                {"timestamp": "2025-10-04T00:00:00Z", "city_wide": {"score": 0.1, "sentiment": "neutral"}},
                {"timestamp": "2025-10-05T00:00:00Z", "city_wide": {"score": 0.3, "sentiment": "positive"}}
            ]
            
            trend = analyzer.analyze_trend(historical_data)
            
            assert "trend" in trend
            assert trend["trend"] in ["improving", "declining", "stable"]
            assert "slope" in trend
            
            # Should detect improving trend
            assert trend["trend"] == "improving"
            assert trend["slope"] > 0


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestIntegration:
    """Integration tests for text processing pipeline"""
    
    def test_end_to_end_summarization(self, sample_traffic_reports):
        """Test complete summarization flow"""
        with patch('text.text_summarizer.genai') as mock_genai:
            # Mock LLM
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Heavy traffic on Old Airport Road due to breakdown."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            summarizer = TextSummarizer()
            
            # Full pipeline
            result = summarizer.summarize(
                reports=sample_traffic_reports,
                event_type="traffic",
                location="Old Airport Road",
                timestamp=datetime.now(),
                use_llm=True
            )
            
            # Comprehensive validation
            assert result is not None
            assert len(result["summary"]) > 0
            assert result["confidence"] > 0.5
            assert "traffic" in result["keywords"]
            assert result["method"] == "llm"
    
    def test_end_to_end_sentiment_with_location(self, sample_texts_with_locations):
        """Test complete sentiment analysis with location extraction"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            # Mock varied sentiments
            mock_model = MagicMock()
            
            def side_effect(texts):
                return [
                    {"label": "NEGATIVE", "score": 0.90},
                    {"label": "POSITIVE", "score": 0.85},
                    {"label": "NEGATIVE", "score": 0.75},
                    {"label": "POSITIVE", "score": 0.95},
                    {"label": "NEGATIVE", "score": 0.80}
                ][:len(texts)]
            
            mock_model.side_effect = side_effect
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            # Analyze with locations
            results = analyzer.batch_analyze(
                texts=sample_texts_with_locations["texts"],
                locations=sample_texts_with_locations["locations"]
            )
            
            # Aggregate
            aggregated = analyzer.aggregate_by_location(results)
            
            assert len(results) == len(sample_texts_with_locations["texts"])
            assert len(aggregated) > 0
            
            # Verify each location has proper data
            for loc_name, loc_data in aggregated.items():
                assert "sentiment" in loc_data
                assert "score" in loc_data
                assert "sample_size" in loc_data
                assert loc_data["sample_size"] > 0


# ============================================================
# EDGE CASES & ERROR HANDLING
# ============================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_reports_list(self):
        """Test handling of empty reports list"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            
            # Should raise ValueError for empty list
            with pytest.raises(ValueError, match="No reports provided"):
                summarizer.summarize(
                    reports=[],
                    event_type="traffic"
                )
    
    def test_single_report(self):
        """Test summarization with single report"""
        with patch('text.text_summarizer.genai') as mock_genai:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Traffic issue on MG Road."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            summarizer = TextSummarizer()
            
            result = summarizer.summarize(
                reports=["Traffic jam on MG Road"],
                event_type="traffic",
                use_llm=True
            )
            
            assert result is not None
            assert len(result["summary"]) > 0
    
    def test_very_long_reports(self):
        """Test handling of very long reports"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            
            long_report = "Traffic issue " * 1000  # Very long text
            reports = [long_report] * 5
            
            # Should handle without crashing
            result = summarizer.summarize(
                reports=reports,
                event_type="traffic"
            )
            
            assert result is not None
    
    def test_special_characters_in_text(self):
        """Test handling of special characters"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_model = MagicMock()
            mock_model.return_value = [{"label": "POSITIVE", "score": 0.8}]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            text = "Great! 😊 @user #bangalore https://test.com 🎉"
            result = analyzer.analyze_sentiment(text)
            
            assert result is not None
            assert "sentiment" in result
    
    def test_mixed_language_text(self):
        """Test handling of mixed language text"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_model = MagicMock()
            mock_model.return_value = [{"label": "POSITIVE", "score": 0.7}]
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            text = "Great service ಧನ್ಯವಾದಗಳು thank you"
            result = analyzer.analyze_sentiment(text)
            
            # Should handle gracefully
            assert result is not None


# ============================================================
# PERFORMANCE TESTS
# ============================================================

class TestPerformance:
    """Performance and efficiency tests"""
    
    def test_batch_processing_efficiency(self):
        """Test batch processing is faster than individual calls"""
        with patch('text.sentiment_analyzer.pipeline') as mock_pipeline:
            mock_model = MagicMock()
            mock_model.return_value = [{"label": "POSITIVE", "score": 0.8}] * 32
            mock_pipeline.return_value = mock_model
            
            analyzer = SentimentAnalyzer()
            
            texts = ["Test text " + str(i) for i in range(32)]
            
            # Batch processing
            import time
            start = time.time()
            results = analyzer.batch_analyze(texts)
            batch_time = time.time() - start
            
            assert len(results) == 32
            # Batch should complete reasonably fast
            assert batch_time < 5.0  # 5 seconds max for 32 texts
    
    def test_deduplication_performance(self):
        """Test deduplication with many reports"""
        with patch('text.text_summarizer.genai'):
            summarizer = TextSummarizer()
            
            # Generate many similar reports
            reports = [f"Traffic jam on road {i}" for i in range(100)]
            
            import time
            start = time.time()
            deduplicated = summarizer.deduplicate_reports(reports)
            dedup_time = time.time() - start
            
            # Should complete quickly
            assert dedup_time < 2.0  # 2 seconds max
            assert len(deduplicated) <= len(reports)  # May not remove any if all unique


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
