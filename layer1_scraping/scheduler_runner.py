"""
Layer 1: Scraping & Storage Orchestrator
Wraps the review processing pipeline for the orchestrator.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from google_play_scraper import reviews

from review_processor import ReviewProcessor

# Setup logging
PROJECT_ROOT = Path(__file__).parent.parent
log_date = datetime.now().strftime('%Y%m%d')
log_file = PROJECT_ROOT / 'logs' / f'scheduler_{log_date}.log'

# Ensure logs directory exists
(PROJECT_ROOT / 'logs').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
APP_ID = 'com.nextbillion.groww'
OUTPUT_DIR = PROJECT_ROOT / 'data'
LOOKBACK_DAYS = 28


class ReviewScheduler:
    """Orchestrates review scraping and processing for Layer 1."""
    
    def __init__(self, start_date: str = None, end_date: str = None):
        self.app_id = APP_ID
        self.processor = ReviewProcessor()
        self.start_date = start_date
        self.end_date = end_date
        logger.info(f"ReviewScheduler initialized with date range: {start_date} to {end_date}" if start_date or end_date else "ReviewScheduler initialized")
    
    def fetch_reviews(self):
        """Fetch reviews from Google Play Store."""
        logger.info(f"Fetching reviews from Google Play Store (App ID: {self.app_id})")
        
        try:
            reviews_list = []
            continuation_token = None
            batch_num = 1
            
            # Fetch reviews in batches using the reviews() function
            while len(reviews_list) < 4000:
                result, continuation_token = reviews(
                    self.app_id,
                    lang='en',
                    country='in',
                    continuation_token=continuation_token
                )
                
                if not result:
                    break
                
                reviews_list.extend(result)
                logger.info(f"Batch {batch_num}: {len(result)} reviews fetched (total: {len(reviews_list)})")
                batch_num += 1
                
                if not continuation_token:
                    break
            
            logger.info(f"Total reviews fetched: {len(reviews_list)}")
            return reviews_list
        
        except Exception as e:
            logger.error(f"Error fetching reviews: {e}")
            raise
    
    def normalize_reviews(self, reviews, start_date: str = None, end_date: str = None):
        """Normalize reviews from API format and filter by date range."""
        normalized = []
        skipped_count = 0
        date_filtered_count = 0
        
        # Parse date range if provided
        start_date_obj = None
        end_date_obj = None
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid start_date format: {start_date}")
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid end_date format: {end_date}")
        
        for idx, review in enumerate(reviews):
            # Filter: Only include reviews with thumbsUpCount (relevance) > 0
            relevance = review.get('thumbsUpCount', 0)
            if relevance <= 0:
                skipped_count += 1
                continue
            
            # Extract date from 'at' field (timestamp), or fall back to other fields
            # The 'at' field is a datetime object from the API
            date_obj = review.get('at')
            if date_obj:
                # If it's a datetime object, convert to string
                if hasattr(date_obj, 'strftime'):
                    date_str = date_obj.strftime('%Y-%m-%d')
                else:
                    # If it's already a string
                    date_str = str(date_obj)[:10]
            else:
                date_str = ''
            
            # Filter by date range if specified
            if start_date_obj or end_date_obj:
                try:
                    review_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if start_date_obj and review_date < start_date_obj:
                        date_filtered_count += 1
                        continue
                    if end_date_obj and review_date > end_date_obj:
                        date_filtered_count += 1
                        continue
                except ValueError:
                    logger.debug(f"Skipping review with invalid date: {date_str}")
                    date_filtered_count += 1
                    continue
            
            # Extract review text - try multiple field names
            text = review.get('reviewText') or review.get('text') or review.get('content') or ''
            
            if not text or len(text.strip()) == 0:
                logger.debug(f"Review {idx}: Empty text, keys available: {list(review.keys())}")
            
            normalized.append({
                'date': date_str,
                'rating': int(review.get('score', 0)),
                'title': review.get('reviewTitle', '') or review.get('title', ''),
                'text': text,
                'relevance': relevance,
            })
        
        logger.info(f"Normalized reviews (relevance > 0): {len(normalized)} out of {len(reviews)} total")
        logger.info(f"Skipped {skipped_count} reviews with zero relevance")
        if date_filtered_count > 0:
            logger.info(f"Filtered out {date_filtered_count} reviews outside date range")
        return normalized
    
    def run_extraction(self):
        """Run the complete Layer 1 extraction pipeline."""
        logger.info("=" * 80)
        logger.info("STARTING WEEKLY REVIEW EXTRACTION TASK")
        logger.info("=" * 80)
        
        try:
            # Fetch reviews
            raw_reviews = self.fetch_reviews()
            
            # Normalize with date filtering
            normalized = self.normalize_reviews(raw_reviews, self.start_date, self.end_date)
            
            # Process
            processed, report = self.processor.process_reviews(normalized)
            
            # Save outputs
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
            # Generate date-based filenames from actual review dates
            if normalized:
                dates = [r.get('date') for r in normalized if r.get('date')]
                dates.sort()
                start_date_str = dates[0].replace('-', '') if dates else datetime.now().strftime('%Y%m%d')
                end_date_str = dates[-1].replace('-', '') if dates else datetime.now().strftime('%Y%m%d')
            else:
                start_date_str = datetime.now().strftime('%Y%m%d')
                end_date_str = datetime.now().strftime('%Y%m%d')
            
            json_file = OUTPUT_DIR / f"review_transformed_{start_date_str}_{end_date_str}.json"
            csv_file = OUTPUT_DIR / f"review_transformed_{start_date_str}_{end_date_str}.csv"
            
            # Save JSON
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({'records': processed}, f, indent=2, ensure_ascii=False)
            
            # Save CSV
            import csv as csv_module
            if processed:
                fieldnames = ['review_id', 'date', 'rating', 'title', 'text', 'clean_text', 'relevance', 'source']
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv_module.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in processed:
                        writer.writerow({k: record.get(k, '') for k in fieldnames})
            
            logger.info(f"Saved JSON: {json_file}")
            logger.info(f"Saved CSV: {csv_file}")
            
            logger.info("\n" + "=" * 80)
            logger.info("TASK COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            return report, str(json_file), str(csv_file)
        
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise


if __name__ == "__main__":
    scheduler = ReviewScheduler()
    report, json_file, csv_file = scheduler.run_extraction()
    print(f"Output JSON: {json_file}")
    print(f"Output CSV: {csv_file}")
