import json
import csv
import logging
import re
import time
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from google.api_core.exceptions import DeadlineExceeded
from classify_config import (
    ALLOWED_THEMES, THEME_KEYWORDS, THEME_PRECEDENCE,
    GEMINI_MODEL, BATCH_SIZE, MAX_RETRIES, CONFIDENCE_THRESHOLD,
    FALLBACK_CONFIDENCE, DEFAULT_THEME, INPUT_FILE,
    OUTPUT_JSON_TEMPLATE, OUTPUT_CSV_TEMPLATE,
    LLM_SYSTEM_PROMPT, LLM_USER_PROMPT_TEMPLATE,
    LOG_FILE, LOG_LEVEL
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReviewClassifier:
    """Classify reviews using Gemini Pro with fallback logic."""
    
    def __init__(self, api_key: str):
        """Initialize with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.fallback_stats = {'count': 0, 'by_theme': defaultdict(int)}
    
    def load_reviews(self, filepath: str) -> List[Dict]:
        """Load reviews from JSON file."""
        logger.info(f"Loading reviews from {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both direct array and wrapped object
        if isinstance(data, dict) and 'records' in data:
            reviews = data['records']
        else:
            reviews = data
        
        logger.info(f"Loaded {len(reviews)} reviews")
        return reviews
    
    def batch_reviews(self, reviews: List[Dict], batch_size: int = BATCH_SIZE) -> List[List[Dict]]:
        """Batch reviews for processing."""
        batches = []
        for i in range(0, len(reviews), batch_size):
            batches.append(reviews[i:i + batch_size])
        logger.info(f"Created {len(batches)} batches of size {batch_size}")
        return batches
    
    def classify_batch_with_llm(self, batch: List[Dict], retry_count: int = 0) -> Tuple[List[Dict], bool]:
        """Call Gemini Pro to classify a batch of reviews."""
        try:
            # Prepare reviews for LLM
            batch_for_llm = []
            for review in batch:
                batch_for_llm.append({
                    'review_id': review['review_id'],
                    'text': review.get('clean_text', '')[:500]  # Limit text length
                })
            
            # Create LLM prompt
            user_prompt = LLM_USER_PROMPT_TEMPLATE.format(
                reviews_json=json.dumps(batch_for_llm, indent=2)
            )
            
            # Call Gemini with exponential backoff for retries
            logger.info(f"Calling Gemini Pro for batch of {len(batch)} reviews (retry {retry_count})")
            response = self.model.generate_content(
                [LLM_SYSTEM_PROMPT, user_prompt],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            
            # Try to extract JSON array
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = response_text[json_start:json_end]
            classifications = json.loads(json_str)
            
            if not isinstance(classifications, list):
                raise ValueError("Response is not a JSON array")
            
            logger.info(f"Successfully classified {len(classifications)} reviews")
            return classifications, True
        
        except DeadlineExceeded as e:
            logger.warning(f"API timeout on batch (attempt {retry_count + 1}): {e}")
            if retry_count < MAX_RETRIES:
                # Exponential backoff: wait before retrying
                wait_time = (2 ** retry_count)  # 1s, 2s, 4s...
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                return self.classify_batch_with_llm(batch, retry_count + 1)
            else:
                logger.warning("Max retries reached for timeout, will use fallback classification")
                return None, False
        
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Invalid LLM response (attempt {retry_count + 1}): {e}")
            
            if retry_count < MAX_RETRIES:
                logger.info("Retrying with stricter instruction...")
                return self.classify_batch_with_llm(batch, retry_count + 1)
            else:
                logger.warning("Max retries reached, will use fallback classification")
                return None, False
    
    def classify_with_keywords(self, text: str) -> Tuple[str, float, str]:
        """Fallback: Classify using keyword matching."""
        text_lower = text.lower()
        matched_themes = set()
        matched_keywords = []
        
        # Check each theme's keywords
        for theme in THEME_PRECEDENCE:
            keywords = THEME_KEYWORDS[theme]
            for keyword in keywords:
                if keyword in text_lower:
                    matched_themes.add(theme)
                    matched_keywords.append(keyword)
                    break
        
        # Apply precedence
        if matched_themes:
            for theme in THEME_PRECEDENCE:
                if theme in matched_themes:
                    keyword_used = next(
                        (k for k in THEME_KEYWORDS[theme] if k in text_lower),
                        'keyword match'
                    )
                    return theme, FALLBACK_CONFIDENCE, f"fallback keyword: {keyword_used}"
        
        # Default
        return DEFAULT_THEME, FALLBACK_CONFIDENCE, "fallback default: no keywords matched"
    
    def validate_and_apply_fallback(self, classifications: List[Dict], batch: List[Dict]) -> List[Dict]:
        """Validate LLM output and apply fallback logic."""
        validated = []
        
        for idx, classif in enumerate(classifications):
            review = batch[idx]
            review_id = classif.get('review_id')
            theme = classif.get('review_theme')
            confidence = classif.get('confidence', 0)
            reason = classif.get('reason', '')
            sentiment = classif.get('sentiment', 'neutral')
            
            # Check if theme is valid
            needs_fallback = (
                not theme or
                theme not in ALLOWED_THEMES or
                confidence < CONFIDENCE_THRESHOLD
            )
            
            if needs_fallback:
                # Apply keyword-based fallback
                fallback_theme, fallback_conf, fallback_reason = self.classify_with_keywords(
                    review.get('clean_text', '')
                )
                
                llm_suggested = theme if theme in ALLOWED_THEMES else None
                
                validated.append({
                    'review_id': review_id,
                    'review_theme': fallback_theme,
                    'sentiment': sentiment,
                    'confidence': max(confidence, fallback_conf) if confidence >= CONFIDENCE_THRESHOLD else fallback_conf,
                    'reason': fallback_reason,
                    'llm_suggested_theme': llm_suggested,
                    'fallback_applied': True
                })
                
                self.fallback_stats['count'] += 1
                self.fallback_stats['by_theme'][fallback_theme] += 1
            else:
                # LLM output was valid
                validated.append({
                    'review_id': review_id,
                    'review_theme': theme,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'reason': reason,
                    'llm_suggested_theme': None,
                    'fallback_applied': False
                })
        
        return validated
    
    def classify_all(self, reviews: List[Dict]) -> List[Dict]:
        """Classify all reviews in batches."""
        all_classified = []
        batches = self.batch_reviews(reviews)
        
        for batch_idx, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_idx}/{len(batches)}")
            
            # Get LLM classifications
            llm_output, success = self.classify_batch_with_llm(batch)
            
            if success and llm_output:
                # Validate and apply fallback
                validated = self.validate_and_apply_fallback(llm_output, batch)
            else:
                # Full fallback classification
                logger.warning(f"Using full fallback for batch {batch_idx}")
                validated = []
                for review in batch:
                    theme, conf, reason = self.classify_with_keywords(review.get('clean_text', ''))
                    validated.append({
                        'review_id': review['review_id'],
                        'review_theme': theme,
                        'sentiment': 'neutral',
                        'confidence': conf,
                        'reason': reason,
                        'llm_suggested_theme': None,
                        'fallback_applied': True
                    })
                    self.fallback_stats['count'] += 1
                    self.fallback_stats['by_theme'][theme] += 1
            
            all_classified.extend(validated)
        
        return all_classified
    
    def enrich_with_source_data(self, classifications: List[Dict], reviews: List[Dict]) -> List[Dict]:
        """Add original review data to classifications."""
        reviews_by_id = {r['review_id']: r for r in reviews}
        
        enriched = []
        for classif in classifications:
            review = reviews_by_id.get(classif['review_id'], {})
            enriched.append({
                'review_id': classif['review_id'],
                'date': review.get('date', ''),
                'rating': review.get('rating', 0),
                'title': review.get('title', ''),
                'text': review.get('text', ''),
                'clean_text': review.get('clean_text', ''),
                'sentiment': classif.get('sentiment'),
                'review_theme': classif['review_theme'],
                'confidence': classif['confidence'],
                'reason': classif['reason'],
                'llm_suggested_theme': classif.get('llm_suggested_theme'),
                'fallback_applied': classif['fallback_applied']
            })
        
        return enriched
    
    def get_date_range(self, reviews: List[Dict]) -> Tuple[str, str]:
        """Extract date range from reviews"""
        dates = [r.get('date') for r in reviews if r.get('date')]
        if dates:
            dates.sort()
            return dates[0], dates[-1]
        return '', ''
    
    def save_json(self, records: List[Dict], reviews: List[Dict]) -> str:
        """Save classified reviews to JSON."""
        # ... existing code ...
        theme_counts = defaultdict(int)
        total_confidence = 0
        fallback_count = 0
        
        for record in records:
            theme_counts[record['review_theme']] += 1
            total_confidence += record['confidence']
            if record['fallback_applied']:
                fallback_count += 1
        
        # Ensure all themes are in counts
        for theme in ALLOWED_THEMES:
            if theme not in theme_counts:
                theme_counts[theme] = 0
        
        output = {
            'records': records,
            'summary': {
                'total_input': len(reviews),
                'total_output': len(records),
                'counts_by_theme': dict(theme_counts),
                're_prompts_or_fallbacks': fallback_count,
                'average_confidence': total_confidence / len(records) if records else 0
            }
        }
        
        # Generate dynamic filename with date range
        start_date, end_date = self.get_date_range(reviews)
        start_date_fmt = start_date.replace('-', '') if start_date else 'unknown'
        end_date_fmt = end_date.replace('-', '') if end_date else 'unknown'
        filepath = f"data/review_classified_{start_date_fmt}_{end_date_fmt}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved JSON to {filepath}")
        return filepath
    
    def save_csv(self, records: List[Dict], reviews: List[Dict]) -> str:
        """Save classified reviews to CSV."""
        # Generate dynamic filename with date range
        start_date, end_date = self.get_date_range(reviews)
        start_date_fmt = start_date.replace('-', '') if start_date else 'unknown'
        end_date_fmt = end_date.replace('-', '') if end_date else 'unknown'
        filepath = f"data/review_classified_{start_date_fmt}_{end_date_fmt}.csv"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'review_id', 'date', 'rating', 'sentiment', 'title', 'text', 'clean_text',
                'review_theme', 'confidence', 'reason', 'llm_suggested_theme', 'fallback_applied'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                writer.writerow(record)
        
        logger.info(f"Saved CSV to {filepath}")
        return filepath
    
    def run(self, api_key: str, input_file: str = None) -> Dict:
        """Run complete classification pipeline.
        
        Args:
            api_key: Gemini API key
            input_file: Optional input file path (uses config INPUT_FILE if not provided)
        """
        logger.info("=" * 80)
        logger.info("Starting Review Classification")
        logger.info("=" * 80)
        
        try:
            # Use provided input_file or fall back to config
            filepath = input_file if input_file else INPUT_FILE
            
            # Load reviews
            reviews = self.load_reviews(filepath)
            
            # Classify all
            classifications = self.classify_all(reviews)
            
            # Enrich with source data
            enriched = self.enrich_with_source_data(classifications, reviews)
            
            # Save outputs
            json_file = self.save_json(enriched, reviews)
            csv_file = self.save_csv(enriched, reviews)
            
            # Print summary
            summary = {
                'total_reviews': len(reviews),
                'total_classified': len(enriched),
                'fallbacks_applied': self.fallback_stats['count'],
                'json_output': json_file,
                'csv_output': csv_file
            }
            
            logger.info("=" * 80)
            logger.info("Classification Complete")
            logger.info(f"Total reviews: {summary['total_reviews']}")
            logger.info(f"Fallbacks applied: {summary['fallbacks_applied']}")
            logger.info(f"JSON: {summary['json_output']}")
            logger.info(f"CSV: {summary['csv_output']}")
            logger.info("=" * 80)
            
            return summary
        
        except Exception as e:
            logger.exception(f"Classification failed: {e}")
            raise

if __name__ == "__main__":
    import os
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY environment variable")
    
    classifier = ReviewClassifier(api_key)
    classifier.run(api_key)
