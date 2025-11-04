"""
Text Similarity Utilities
For deduplication and event matching
"""
from typing import List, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fuzzywuzzy import fuzz

from utils.logger import setup_logger

logger = setup_logger(__name__)


class TextSimilarity:
    """
    Text similarity calculator using multiple methods:
    1. TF-IDF + Cosine Similarity (semantic similarity)
    2. Fuzzy string matching (exact/partial matches)
    3. Jaccard similarity (word overlap)
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            max_features=1000
        )
        self.fitted = False
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for comparison
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def calculate_tfidf_similarity(self, texts: List[str]) -> np.ndarray:
        """
        Calculate TF-IDF based cosine similarity matrix
        
        Args:
            texts: List of text strings
        
        Returns:
            Similarity matrix (n x n)
        """
        if len(texts) < 2:
            return np.array([[1.0]])
        
        try:
            # Preprocess all texts
            processed = [self.preprocess_text(t) for t in texts]
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(processed)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            return similarity_matrix
        
        except Exception as e:
            logger.error(f"Error calculating TF-IDF similarity: {e}")
            # Return identity matrix as fallback
            return np.eye(len(texts))
    
    def calculate_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate fuzzy string similarity (0-1)
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)
        
        # Use fuzz ratio (0-100), normalize to 0-1
        ratio = fuzz.ratio(text1, text2) / 100.0
        
        # Also check partial ratio (substring matching)
        partial_ratio = fuzz.partial_ratio(text1, text2) / 100.0
        
        # Take the maximum
        return max(ratio, partial_ratio)
    
    def calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity (word overlap)
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Jaccard similarity (0-1)
        """
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)
        
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_combined_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate combined similarity using multiple methods
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Combined similarity score (0-1)
        """
        # TF-IDF similarity
        tfidf_sim = self.calculate_tfidf_similarity([text1, text2])[0, 1]
        
        # Fuzzy similarity
        fuzzy_sim = self.calculate_fuzzy_similarity(text1, text2)
        
        # Jaccard similarity
        jaccard_sim = self.calculate_jaccard_similarity(text1, text2)
        
        # Weighted average (TF-IDF gets more weight)
        combined = (0.5 * tfidf_sim + 0.3 * fuzzy_sim + 0.2 * jaccard_sim)
        
        return combined
    
    def find_similar_pairs(
        self, 
        texts: List[str], 
        threshold: float = 0.8
    ) -> List[Tuple[int, int, float]]:
        """
        Find pairs of similar texts above threshold
        
        Args:
            texts: List of texts to compare
            threshold: Similarity threshold (0-1)
        
        Returns:
            List of (index1, index2, similarity) tuples
        """
        similar_pairs = []
        
        # Calculate similarity matrix
        sim_matrix = self.calculate_tfidf_similarity(texts)
        
        # Find pairs above threshold
        n = len(texts)
        for i in range(n):
            for j in range(i + 1, n):
                similarity = sim_matrix[i, j]
                if similarity >= threshold:
                    similar_pairs.append((i, j, similarity))
        
        # Sort by similarity (descending)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return similar_pairs


# Global instance
text_similarity = TextSimilarity()


if __name__ == "__main__":
    # Test similarity
    texts = [
        "Heavy traffic on MG Road due to accident",
        "Traffic jam at MG Road after accident",
        "Power outage in Koramangala",
        "Electricity cut in Koramangala area"
    ]
    
    print("Testing Text Similarity\n" + "="*50)
    
    # Find similar pairs
    similarity = TextSimilarity()
    pairs = similarity.find_similar_pairs(texts, threshold=0.5)
    
    print(f"\nFound {len(pairs)} similar pairs:\n")
    for i, j, score in pairs:
        print(f"Similarity: {score:.2f}")
        print(f"  Text 1: {texts[i]}")
        print(f"  Text 2: {texts[j]}")
        print()
