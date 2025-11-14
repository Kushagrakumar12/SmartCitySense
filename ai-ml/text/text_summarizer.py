"""
Text Summarization Module - Member B1
LLM-powered summarization using Gemini or GPT to combine multiple reports

Features:
- Combine multiple reports about same incident into one summary
- Custom prompts for different event types
- Fallback template-based summarization
- Deduplication and preprocessing
- Location and time normalization
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

# LLM Integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Langchain for orchestration
try:
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from utils.logger import logger
from config.config import config


class TextSummarizer:
    """
    LLM-powered text summarization for combining multiple citizen reports
    """
    
    def __init__(self):
        """Initialize text summarizer with LLM configuration"""
        logger.info("Initializing Text Summarizer...")
        
        self.config = config.text
        self.llm_provider = self.config.summarization_llm_provider
        self.model_name = self.config.summarization_model_name
        
        # Initialize LLM
        self.llm = None
        self._initialize_llm()
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        # Template fallback patterns
        self.fallback_templates = self._create_fallback_templates()
        
        logger.success(f"✅ Text Summarizer initialized with {self.llm_provider}")
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        try:
            if self.llm_provider == "gemini" and GEMINI_AVAILABLE:
                api_key = self.config.google_api_key
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in environment")
                
                genai.configure(api_key=api_key)
                
                if LANGCHAIN_AVAILABLE:
                    self.llm = ChatGoogleGenerativeAI(
                        model=self.model_name,
                        temperature=0.3,
                        max_tokens=512,
                        google_api_key=api_key
                    )
                else:
                    self.llm = genai.GenerativeModel(self.model_name)
                
                logger.info(f"Initialized Gemini model: {self.model_name}")
                
            elif self.llm_provider == "openai" and OPENAI_AVAILABLE:
                api_key = self.config.openai_api_key
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                
                if LANGCHAIN_AVAILABLE:
                    self.llm = ChatOpenAI(
                        model=self.model_name,
                        temperature=0.3,
                        max_tokens=512,
                        openai_api_key=api_key
                    )
                else:
                    self.llm = OpenAI(api_key=api_key)
                
                logger.info(f"Initialized OpenAI model: {self.model_name}")
            
            else:
                logger.warning("No LLM provider available, using fallback templates only")
                self.llm = None
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            logger.warning("Falling back to template-based summarization")
            self.llm = None
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load custom prompts for each event type"""
        prompts = {
            "traffic": """You are analyzing traffic reports from citizens in Bengaluru.
            
Multiple reports about a traffic incident:
{reports}

Location: {location}
Time: {time}

Create a concise, informative summary (max 2 sentences) that:
1. States the main issue
2. Provides actionable information (when to avoid, alternative routes if mentioned)
3. Uses simple, clear language

Summary:""",
            
            "power": """You are analyzing power outage reports from citizens in Bengaluru.

Multiple reports about power issues:
{reports}

Location: {location}
Time: {time}

Create a concise summary (max 2 sentences) that:
1. States the power issue (outage, fluctuation, etc.)
2. Mentions affected areas
3. Includes estimated restoration time if mentioned

Summary:""",
            
            "civic": """You are analyzing civic complaints from citizens in Bengaluru.

Multiple complaints:
{reports}

Location: {location}
Time: {time}

Create a concise summary (max 2 sentences) that:
1. States the main civic issue
2. Mentions severity if critical
3. Uses professional, neutral tone

Summary:""",
            
            "weather": """You are analyzing weather-related reports from citizens in Bengaluru.

Multiple weather reports:
{reports}

Location: {location}
Time: {time}

Create a concise summary (max 2 sentences) that:
1. States the weather condition
2. Mentions impact on daily activities
3. Includes safety information if relevant

Summary:""",
            
            "cultural": """You are analyzing cultural event reports from citizens in Bengaluru.

Multiple event reports:
{reports}

Location: {location}
Time: {time}

Create a concise summary (max 2 sentences) that:
1. States the event name and type
2. Mentions key details (time, venue)
3. Uses engaging, informative tone

Summary:""",
            
            "default": """You are analyzing citizen reports about a city incident in Bengaluru.

Multiple reports:
{reports}

Location: {location}
Time: {time}

Create a concise, factual summary (max 2 sentences) combining the key information.

Summary:"""
        }
        
        return prompts
    
    def _create_fallback_templates(self) -> Dict[str, str]:
        """Create template-based fallback patterns"""
        templates = {
            "traffic": "{count} reports of {issue} near {location}. {action}",
            "power": "Power {issue} reported in {location} affecting {count} users. {action}",
            "civic": "{count} complaints about {issue} in {location}. {action}",
            "weather": "{condition} reported in {location}. {action}",
            "cultural": "{event} happening in {location}. {action}",
            "default": "{count} reports about {issue} in {location}. {action}"
        }
        
        return templates
    
    def preprocess_reports(self, reports: List[str]) -> List[str]:
        """
        Preprocess and clean text reports
        
        Args:
            reports: List of raw text reports
            
        Returns:
            List of cleaned reports
        """
        cleaned = []
        
        for report in reports:
            # Remove URLs
            text = re.sub(r'http\S+|www\.\S+', '', report)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep basic punctuation
            text = re.sub(r'[^\w\s.,!?-]', '', text)
            
            # Strip and lowercase
            text = text.strip()
            
            # Skip very short reports (likely noise)
            if len(text) > 10:
                cleaned.append(text)
        
        return cleaned
    
    def deduplicate_reports(self, reports: List[str]) -> List[str]:
        """
        Remove duplicate and near-duplicate reports
        
        Args:
            reports: List of text reports
            
        Returns:
            Deduplicated list
        """
        if not reports:
            return []
        
        # Exact duplicates
        unique = list(set(reports))
        
        # Near-duplicate detection (simple Jaccard similarity)
        final = []
        for i, report in enumerate(unique):
            words_i = set(report.lower().split())
            is_duplicate = False
            
            for j in range(len(final)):
                words_j = set(final[j].lower().split())
                intersection = len(words_i & words_j)
                union = len(words_i | words_j)
                
                if union > 0:
                    similarity = intersection / union
                    if similarity > 0.8:  # 80% similarity threshold
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                final.append(report)
        
        return final
    
    def extract_common_keywords(self, reports: List[str], top_n: int = 5) -> List[str]:
        """Extract most common keywords from reports"""
        # Stopwords (basic English + common Kannada transliterations)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'them', 'their', 'there', 'here', 'very',
            'just', 'now', 'then', 'than', 'so', 'also', 'only', 'from', 'about'
        }
        
        all_words = []
        for report in reports:
            words = re.findall(r'\b\w+\b', report.lower())
            all_words.extend([w for w in words if w not in stopwords and len(w) > 2])
        
        # Count and return top keywords
        counter = Counter(all_words)
        return [word for word, count in counter.most_common(top_n)]
    
    def normalize_location(self, location: str) -> str:
        """Normalize location names"""
        # Common abbreviations and variations
        replacements = {
            'blr': 'bangalore',
            'blore': 'bangalore',
            'namma bengaluru': 'bengaluru',
            'mg road': 'mahatma gandhi road',
            'kr': 'krishnarajapuram',
            'indiranagar': 'indiranagar',
        }
        
        location_lower = location.lower()
        for old, new in replacements.items():
            location_lower = location_lower.replace(old, new)
        
        return location_lower.title()
    
    def summarize_with_llm(
        self,
        reports: List[str],
        event_type: str,
        location: str,
        timestamp: Optional[datetime] = None
    ) -> Tuple[str, float]:
        """
        Generate summary using LLM
        
        Args:
            reports: List of preprocessed reports
            event_type: Type of event (traffic, power, etc.)
            location: Location of incident
            timestamp: Timestamp of reports
            
        Returns:
            Tuple of (summary_text, confidence_score)
        """
        if not self.llm:
            raise ValueError("LLM not initialized")
        
        # Prepare input
        reports_text = "\n".join([f"- {report}" for report in reports])
        time_str = timestamp.strftime("%I:%M %p, %B %d") if timestamp else "Recent"
        
        # Get appropriate prompt
        prompt_template = self.prompts.get(event_type, self.prompts["default"])
        prompt = prompt_template.format(
            reports=reports_text,
            location=location,
            time=time_str
        )
        
        try:
            # Call LLM based on provider
            if self.llm_provider == "gemini":
                if LANGCHAIN_AVAILABLE:
                    response = self.llm.invoke(prompt)
                    summary = response.content.strip()
                else:
                    response = self.llm.generate_content(prompt)
                    summary = response.text.strip()
            
            elif self.llm_provider == "openai":
                if LANGCHAIN_AVAILABLE:
                    response = self.llm.invoke(prompt)
                    summary = response.content.strip()
                else:
                    response = self.llm.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=512
                    )
                    summary = response.choices[0].message.content.strip()
            
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
            
            # Calculate confidence based on summary quality
            confidence = self._calculate_confidence(summary, reports)
            
            logger.info(f"Generated summary with confidence {confidence:.2f}")
            return summary, confidence
            
        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            raise
    
    def summarize_with_template(
        self,
        reports: List[str],
        event_type: str,
        location: str
    ) -> Tuple[str, float]:
        """
        Generate summary using template (fallback method)
        
        Args:
            reports: List of preprocessed reports
            event_type: Type of event
            location: Location of incident
            
        Returns:
            Tuple of (summary_text, confidence_score)
        """
        # Extract key information
        keywords = self.extract_common_keywords(reports, top_n=3)
        issue = keywords[0] if keywords else "incident"
        
        # Determine action based on event type and keywords
        action = "Please exercise caution."
        if event_type == "traffic":
            action = "Consider alternative routes."
        elif event_type == "power":
            action = "Restoration efforts underway."
        elif event_type == "civic":
            action = "Authorities notified."
        
        # Get template and fill
        template = self.fallback_templates.get(event_type, self.fallback_templates["default"])
        
        summary = template.format(
            count=len(reports),
            issue=issue,
            location=location,
            action=action,
            condition=issue if event_type == "weather" else "",
            event=issue if event_type == "cultural" else ""
        )
        
        # Lower confidence for template-based
        confidence = 0.70
        
        logger.info(f"Generated template summary with confidence {confidence:.2f}")
        return summary, confidence
    
    def _calculate_confidence(self, summary: str, reports: List[str]) -> float:
        """
        Calculate confidence score for generated summary
        
        Factors:
        - Length appropriateness
        - Keyword coverage
        - Completeness
        """
        confidence = 0.0
        
        # Length check (50-200 chars ideal)
        summary_len = len(summary)
        if 50 <= summary_len <= 200:
            confidence += 0.3
        elif 30 <= summary_len <= 250:
            confidence += 0.2
        else:
            confidence += 0.1
        
        # Keyword coverage
        keywords = self.extract_common_keywords(reports, top_n=5)
        summary_lower = summary.lower()
        coverage = sum(1 for kw in keywords if kw in summary_lower) / max(len(keywords), 1)
        confidence += coverage * 0.4
        
        # Has actionable information (heuristic)
        actionable_words = ['avoid', 'until', 'reported', 'expected', 'please', 'caution']
        if any(word in summary_lower for word in actionable_words):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def summarize(
        self,
        reports: List[str],
        event_type: str = "default",
        location: str = "Bengaluru",
        timestamp: Optional[datetime] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Main summarization function
        
        Args:
            reports: List of raw text reports
            event_type: Type of event (traffic, power, civic, weather, cultural)
            location: Location of incident
            timestamp: Timestamp of reports
            use_llm: Whether to use LLM (if False, uses template)
            
        Returns:
            Dictionary with summary, confidence, metadata
        """
        try:
            # Validate input
            if not reports:
                raise ValueError("No reports provided")
            
            # Preprocessing
            logger.info(f"Processing {len(reports)} reports for {event_type} in {location}")
            cleaned_reports = self.preprocess_reports(reports)
            deduplicated_reports = self.deduplicate_reports(cleaned_reports)
            
            if not deduplicated_reports:
                raise ValueError("No valid reports after preprocessing")
            
            logger.info(f"After preprocessing: {len(deduplicated_reports)} unique reports")
            
            # Normalize location
            normalized_location = self.normalize_location(location)
            
            # Generate summary
            if use_llm and self.llm is not None:
                try:
                    summary, confidence = self.summarize_with_llm(
                        deduplicated_reports,
                        event_type,
                        normalized_location,
                        timestamp
                    )
                except Exception as e:
                    logger.warning(f"LLM failed, falling back to template: {e}")
                    summary, confidence = self.summarize_with_template(
                        deduplicated_reports,
                        event_type,
                        normalized_location
                    )
            else:
                summary, confidence = self.summarize_with_template(
                    deduplicated_reports,
                    event_type,
                    normalized_location
                )
            
            # Prepare result
            result = {
                "event_type": event_type,
                "summary": summary,
                "confidence": round(confidence, 3),
                "location": normalized_location,
                "timestamp": (timestamp or datetime.now()).isoformat(),
                "source_count": len(reports),
                "processed_count": len(deduplicated_reports),
                "keywords": self.extract_common_keywords(deduplicated_reports, top_n=5),
                "method": "llm" if (use_llm and self.llm) else "template"
            }
            
            logger.success(f"✅ Summarization complete: {summary[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            raise
    
    def batch_summarize(
        self,
        grouped_reports: Dict[str, List[str]],
        event_type: str = "default",
        location: str = "Bengaluru"
    ) -> List[Dict[str, Any]]:
        """
        Batch process multiple report groups
        
        Args:
            grouped_reports: Dict of {group_id: [reports]}
            event_type: Event type
            location: Location
            
        Returns:
            List of summary results
        """
        results = []
        
        for group_id, reports in grouped_reports.items():
            try:
                result = self.summarize(reports, event_type, location)
                result["group_id"] = group_id
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to summarize group {group_id}: {e}")
        
        logger.info(f"Batch summarized {len(results)}/{len(grouped_reports)} groups")
        return results
