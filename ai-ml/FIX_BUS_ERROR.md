# 🔧 Fix for Bus Error on Apple Silicon (ARM64)

## Problem
You're experiencing a **bus error** when running PyTorch models on:
- **Python 3.13** (very new, unstable with PyTorch)
- **Apple Silicon (ARM64)** Mac
- **PyTorch 2.6.0+**

This is a known issue: **Python 3.13 + PyTorch + ARM64 = Bus Error**

## ✅ Solution 1: Use Python 3.11 (RECOMMENDED)

Python 3.13 is too new and has compatibility issues with PyTorch on ARM64.

### Steps:

```bash
# 1. Install Python 3.11 using Homebrew
brew install python@3.11

# 2. Navigate to your project
cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml

# 3. Remove old virtual environment
rm -rf venv

# 4. Create new venv with Python 3.11
/opt/homebrew/bin/python3.11 -m venv venv

# 5. Activate the new environment
source venv/bin/activate

# 6. Upgrade pip
pip install --upgrade pip

# 7. Install dependencies
pip install -r requirements.txt

# 8. Test sentiment analyzer
python -c "
from text.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze_sentiment('I love Bangalore!')
print('Sentiment:', result['sentiment'])
print('Score:', result['score'])
print('✅ SUCCESS!')
"
```

## ✅ Solution 2: Use Conda with Python 3.11

```bash
# 1. Create conda environment with Python 3.11
conda create -n smartcitysense python=3.11 -y

# 2. Activate
conda activate smartcitysense

# 3. Navigate to project
cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml

# 4. Install dependencies
pip install -r requirements.txt

# 5. Test
python -c "
from text.sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
result = analyzer.analyze_sentiment('I love Bangalore!')
print('✅ SUCCESS! Sentiment:', result['sentiment'])
"
```

## ✅ Solution 3: Use Docker (if you have it)

```bash
# Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
EOF

# Build and run
docker build -t smartcitysense .
docker run -p 8001:8001 smartcitysense
```

## Alternative: Use TextBlob (Simple Fallback)

If you can't change Python version right now, I can implement a simpler sentiment analyzer using TextBlob that doesn't use PyTorch:

```python
from textblob import TextBlob

def simple_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1
    
    if polarity > 0.1:
        return {"sentiment": "positive", "score": polarity}
    elif polarity < -0.1:
        return {"sentiment": "negative", "score": polarity}
    else:
        return {"sentiment": "neutral", "score": polarity}
```

## Why This Happens

- **Python 3.13** was released very recently (October 2024)
- **PyTorch** hasn't fully optimized for Python 3.13 on ARM64
- **Memory alignment issues** cause bus errors on Apple Silicon
- **Known bug**: https://github.com/pytorch/pytorch/issues/114602

## Recommended Action

**Use Python 3.11** - it's stable, well-tested, and fully compatible with PyTorch on ARM64.

---

## Quick Check: Which Python are you using?

```bash
python --version      # Check default Python
python3 --version     # Check Python 3
which python3         # Where is it installed?
arch                  # Verify architecture (should show arm64)
```

---

Let me know which solution you want to try!
