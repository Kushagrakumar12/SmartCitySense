"""
Utils module initialization
"""
from .logger import setup_logger, logger
from .text_similarity import TextSimilarity, text_similarity
from .validators import DataValidator, ProcessedEvent, Coordinates

__all__ = [
    'setup_logger',
    'logger',
    'TextSimilarity',
    'text_similarity',
    'DataValidator',
    'ProcessedEvent',
    'Coordinates'
]
