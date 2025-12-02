import json
import uuid
import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from pathlib import Path

# Configuration
MIN_WORD_COUNT = 10
LOOKBACK_DAYS = 28
APP_ID = 'com.nextbillion.groww'

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'data'
LOG_FILE = PROJECT_ROOT / 'logs' / 'scheduler.log'

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(PROJECT_ROOT / 'logs').mkdir(parents=True, exist_ok=True)

LOG_LEVEL = 'INFO'

PII_REDACTION = {
    'email': '[EMAIL_REDACTED]',
    'phone': '[PHONE_REDACTED]',
    'id': '[ID_REDACTED]',
    'person': '[USER_REDACTED]'
}

TYPO_CORRECTIONS = {
    'zerodha': 'zerodha',
    'groww': 'groww',
    'dhan': 'dhan',
    'thinkorswim': 'thinkorswim',
    'grok': 'error',
    'crap': 'bad',
    'sucks': 'bad',
    'worst': 'worst',
    'gud': 'good',
    'awsome': 'awesome',
    'excelent': 'excellent',
    'wasteofmoney': 'waste',
    'scam': 'scam',
    'fraudsters': 'fraud',
    'beware': 'beware',
    'cheat': 'cheat',
    'steal': 'steal',
    'looted': 'looted',
    'fooled': 'fooled',
    'tricked': 'tricked',
    'lmao': 'haha'
}

CSV_COLUMNS = ['review_id', 'date', 'rating', 'title', 'text', 'clean_text', 'relevance', 'source']

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReviewProcessor:
    """Process Google Play reviews with PII redaction, text cleaning, and weekly bucketing."""
    
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+91|0)?[6-9]\d{9}\b|\b\d{10}\b',
            'pan': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
            'aadhaar': r'\b\d{4}\s?\d{4}\s?\d{4}\b',
            'account': r'\b\d{6,}\b',
            'username': r'@[a-zA-Z0-9_]+|[a-zA-Z_][a-zA-Z0-9_]*[0-9]{3,}',
        }
    
    def redact_pii(self, text):
        """Detect and redact PII from text."""
        if not text:
            return text
        
        # Redact emails
        text = re.sub(self.pii_patterns['email'], PII_REDACTION['email'], text)
        
        # Redact phone numbers
        text = re.sub(self.pii_patterns['phone'], PII_REDACTION['phone'], text)
        
        # Redact PAN
        text = re.sub(self.pii_patterns['pan'], PII_REDACTION['id'], text)
        
        # Redact Aadhaar
        text = re.sub(self.pii_patterns['aadhaar'], PII_REDACTION['id'], text)
        
        # Redact account numbers (6+ digits)
        text = re.sub(self.pii_patterns['account'], PII_REDACTION['id'], text)
        
        # Redact usernames
        text = re.sub(self.pii_patterns['username'], PII_REDACTION['person'], text)
        
        return text
    
    def remove_emojis(self, text):
        """Remove emoji characters from text."""
        if not text:
            return text
        
        result = []
        for char in text:
            code = ord(char)
            # Skip emoji/symbol Unicode ranges
            if (0x1F000 <= code <= 0x1F9FF or  # Emoticons, Symbols, Pictographs
                0x2600 <= code <= 0x27BF or    # Miscellaneous Symbols and Dingbats
                0x2300 <= code <= 0x23FF or    # Miscellaneous Technical
                0xFE0F == code):               # Variation Selector
                continue
            result.append(char)
        return ''.join(result)
    
    def clean_text(self, text):
        """Normalize text: lowercase, trim, normalize punctuation, correct typos."""
        if not text:
            return ""
        
        # Remove emojis first
        text = self.remove_emojis(text)
        
        # Normalize fancy quotes
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\u201C', '"').replace('\u201D', '"')
        
        # Lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Apply typo corrections
        for typo, correct in TYPO_CORRECTIONS.items():
            text = re.sub(r'\b' + typo + r'\b', correct, text)
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def count_words(self, text):
        """Count words in text."""
        return len(text.split())
    
    def get_week_boundaries(self, date_obj):
        """Get Monday (week_start) and Sunday (week_end) for the given date."""
        weekday = date_obj.weekday()  # Monday=0, Sunday=6
        week_start = date_obj - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    def process_reviews(self, raw_reviews):
        """
        Process raw reviews: PII redaction, text cleaning, deduplication, filtering.
        Returns: (processed_reviews, report)
        """
        
        logger.info(f"Starting review processing for {len(raw_reviews)} reviews")
        
        # Parse and prepare for deduplication
        parsed_reviews = []
        for review in raw_reviews:
            date_str = review.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                logger.warning(f"Skipping review with invalid date: {date_str}")
                continue
            
            text = review.get('text', '')
            
            # Redact PII
            redacted_text = self.redact_pii(text)
            
            # Clean text
            clean = self.clean_text(redacted_text)
            
            # Check minimum word count after cleaning
            word_count = self.count_words(clean)
            if word_count < MIN_WORD_COUNT:
                logger.debug(f"Skipping review with {word_count} words (min: {MIN_WORD_COUNT})")
                continue
            
            parsed_reviews.append({
                'date': date_obj,
                'date_str': date_str,
                'rating': review.get('rating', 0),
                'title': review.get('title', ''),
                'text': redacted_text,
                'clean_text': clean,
                'relevance': review.get('relevance', 0),
                'clean_lower': clean.lower().strip(),  # for deduplication
                'word_count': word_count
            })
        
        logger.info(f"After minimum word count filter: {len(parsed_reviews)} reviews")
        
        # Deduplicate by clean text - keep earliest date
        seen = {}
        deduplicated = []
        duplicates_removed = 0
        
        for review in parsed_reviews:
            clean_key = review['clean_lower']
            if clean_key not in seen:
                seen[clean_key] = review
                deduplicated.append(review)
            else:
                # Keep the one with earlier date
                if review['date'] < seen[clean_key]['date']:
                    deduplicated.remove(seen[clean_key])
                    deduplicated.append(review)
                    seen[clean_key] = review
                duplicates_removed += 1
        
        logger.info(f"Duplicates removed: {duplicates_removed}")
        logger.info(f"After deduplication: {len(deduplicated)} reviews")
        
        # Transform into final schema
        transformed = []
        for review in deduplicated:
            week_start, week_end = self.get_week_boundaries(review['date'])
            
            record = {
                'review_id': str(uuid.uuid4()),
                'date': review['date_str'],
                'week_start_date': week_start.strftime('%Y-%m-%d'),
                'week_end_date': week_end.strftime('%Y-%m-%d'),
                'rating': review['rating'],
                'title': review['title'],
                'text': review['text'],
                'clean_text': review['clean_text'],
                'relevance': review['relevance'],
                'source': 'google_play'
            }
            transformed.append(record)
        
        # Sort by date
        transformed.sort(key=lambda x: x['date'])
        
        # Generate report
        report = self.generate_report(raw_reviews, transformed, len(parsed_reviews), duplicates_removed)
        
        logger.info(f"Processing complete: {len(transformed)} final reviews")
        
        return transformed, report
    
    def generate_report(self, raw_reviews, transformed, after_filter, duplicates_removed):
        """Generate summary report."""
        
        week_buckets = defaultdict(int)
        rating_dist = defaultdict(int)
        
        for record in transformed:
            week_key = (record['week_start_date'], record['week_end_date'])
            week_buckets[week_key] += 1
            rating_dist[record['rating']] += 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_input': len(raw_reviews),
            'after_min_word_filter': after_filter,
            'duplicates_removed': duplicates_removed,
            'total_output': len(transformed),
            'filters_applied': {
                'min_word_count': MIN_WORD_COUNT,
                'pii_redaction': True,
                'emoji_removal': True,
                'text_normalization': True,
                'deduplication': True
            },
            'rating_distribution': dict(sorted(rating_dist.items())),
            'weekly_distribution': [
                {
                    'week_start': week[0],
                    'week_end': week[1],
                    'count': count
                }
                for week, count in sorted(week_buckets.items())
            ],
            'example_records': transformed[:3] if transformed else []
        }
        
        return report
    
    def save_json(self, data, filename):
        """Save data to JSON file."""
        filepath = f"{OUTPUT_DIR}{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON: {filepath}")
        return filepath
    
    def save_csv(self, data, filename):
        """Save data to CSV file."""
        filepath = f"{OUTPUT_DIR}{filename}"
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for row in data:
                # Only include columns in CSV_COLUMNS
                csv_row = {col: row.get(col, '') for col in CSV_COLUMNS}
                writer.writerow(csv_row)
        logger.info(f"Saved CSV: {filepath}")
        return filepath
    
    def print_report(self, report):
        """Print formatted report."""
        print("\n" + "="*80)
        print("REVIEW PROCESSING REPORT")
        print("="*80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"\nTotal reviews input: {report['total_input']}")
        print(f"After minimum word count filter ({MIN_WORD_COUNT} words): {report['after_min_word_filter']}")
        print(f"Duplicates removed: {report['duplicates_removed']}")
        print(f"Total reviews output: {report['total_output']}")
        
        print(f"\nFilters Applied:")
        for filter_name, applied in report['filters_applied'].items():
            status = "Yes" if applied else "No"
            print(f"  - {filter_name}: {status}")
        
        print(f"\nRating Distribution (output):")
        for rating in range(1, 6):
            count = report['rating_distribution'].get(rating, 0)
            print(f"  {rating}-star: {count} reviews")
        
        print(f"\nWeekly Distribution:")
        for week in report['weekly_distribution']:
            print(f"  {week['week_start']} to {week['week_end']}: {week['count']} reviews")
        
        print(f"\nExample 3 Transformed Records:")
        print("-"*80)
        for i, record in enumerate(report['example_records'][:3], 1):
            print(f"\nExample {i}:")
            print(f"  review_id: {record['review_id']}")
            print(f"  date: {record['date']}")
            print(f"  week: {record['week_start_date']} to {record['week_end_date']}")
            print(f"  rating: {record['rating']}-star")
            print(f"  title (version): {record['title']}")
            print(f"  text: {record['text'][:100]}...")
            print(f"  clean_text: {record['clean_text'][:100]}...")
            print(f"  relevance: {record['relevance']}")
            print(f"  source: {record['source']}")
        
        print("\n" + "="*80 + "\n")
