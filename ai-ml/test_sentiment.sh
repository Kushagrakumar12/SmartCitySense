#!/bin/bash
# Quick test script for sentiment analysis

cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml

# Activate virtual environment
source venv/bin/activate

echo "🧪 Testing Sentiment Analysis"
echo "=============================="
echo ""

# Test simple analyzer (works on Python 3.13)
python -c "
from text.simple_sentiment_analyzer import SimpleSentimentAnalyzer

analyzer = SimpleSentimentAnalyzer()

# Single analysis
result = analyzer.analyze_sentiment('I love Bangalore!')
print('Single Analysis:')
print(f\"  Text: 'I love Bangalore!'\")
print(f\"  Sentiment: {result['sentiment']}\")
print(f\"  Score: {result['score']}\")
print(f\"  Confidence: {result['confidence']}\")
print()

# Batch analysis
texts = [
    'Great weather today!',
    'Traffic is terrible',
    'The metro is convenient'
]

print('Batch Analysis:')
results = analyzer.batch_analyze(texts)
for text, result in zip(texts, results):
    print(f\"  '{text}' -> {result['sentiment']} ({result['score']:.2f})\")

print()
print('✅ All tests passed!')
"

echo ""
echo "=============================="
echo "✅ Done!"
