"""
Layer 3: Weekly Pulse Generator
MAP-REDUCE pipeline for generating actionable weekly insights from classified reviews
"""

import json
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import google.generativeai as genai
from .insights_config import (
    INPUT_FILE, OUTPUT_THEME_SUMMARIES, OUTPUT_PULSE_NOTE,
    MAP_CHUNK_SIZE, TOP_THEMES_COUNT, MAX_QUOTES_PER_THEME, MAX_WORD_COUNT,
    GEMINI_MODEL, MAP_PROMPT_TEMPLATE, REDUCE_PROMPT_TEMPLATE,
    LOG_FILE, LOG_LEVEL, ALLOWED_THEMES
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

class WeeklyPulseGenerator:
    """MAP-REDUCE pipeline for weekly insights generation"""
    
    def __init__(self, api_key: str = None, input_file: str = None):
        """Initialize with optional Gemini API key and input file path"""
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        else:
            self.model = None
        self.input_file = input_file or INPUT_FILE
        logger.info(f"WeeklyPulseGenerator initialized with input file: {self.input_file}")
    
    def load_classified_reviews(self) -> List[Dict]:
        """Load classified reviews from Layer 2 output"""
        logger.info(f"Loading classified reviews from {self.input_file}")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'records' in data:
            records = data['records']
        else:
            records = data
        
        logger.info(f"Loaded {len(records)} classified reviews")
        return records
    
    def group_by_theme(self, reviews: List[Dict]) -> Dict[str, List[Dict]]:
        """Group reviews by theme and count them"""
        themes = defaultdict(list)
        for review in reviews:
            theme = review.get('review_theme', 'Unknown')
            themes[theme].append(review)
        
        # Log theme distribution
        for theme, reviews_list in sorted(themes.items(), key=lambda x: -len(x[1])):
            logger.info(f"  {theme}: {len(reviews_list)} reviews")
        
        return dict(themes)
    
    def get_top_themes(self, themed_reviews: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Select top 3 themes by review count"""
        sorted_themes = sorted(themed_reviews.items(), key=lambda x: -len(x[1]))
        top_themes = dict(sorted_themes[:TOP_THEMES_COUNT])
        
        logger.info(f"Selected top {TOP_THEMES_COUNT} themes:")
        for theme, reviews_list in top_themes.items():
            logger.info(f"  {theme}: {len(reviews_list)} reviews")
        
        return top_themes
    
    def chunk_reviews(self, reviews: List[Dict], chunk_size: int = MAP_CHUNK_SIZE) -> List[List[Dict]]:
        """Break reviews into chunks"""
        chunks = []
        for i in range(0, len(reviews), chunk_size):
            chunks.append(reviews[i:i + chunk_size])
        return chunks
    
    def run_map_stage(self, theme: str, reviews: List[Dict]) -> Dict:
        """MAP stage: Extract key points and quotes per theme"""
        logger.info(f"MAP stage for {theme} ({len(reviews)} reviews)")
        
        chunks = self.chunk_reviews(reviews)
        all_key_points = []
        all_quotes = []
        
        for chunk_idx, chunk in enumerate(chunks, 1):
            logger.info(f"  Processing chunk {chunk_idx}/{len(chunks)}")
            
            # Prepare reviews text
            reviews_text = "\n".join([f"- {r.get('clean_text', '')[:200]}" for r in chunk])
            
            # Create MAP prompt
            map_prompt = MAP_PROMPT_TEMPLATE.format(
                theme_name=theme,
                reviews_list=reviews_text
            )
            
            try:
                # Call Gemini
                response = self.model.generate_content(map_prompt)
                response_text = response.text.strip()
                
                # Extract JSON
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    chunk_result = json.loads(json_str)
                    
                    all_key_points.extend(chunk_result.get('key_points', []))
                    all_quotes.extend(chunk_result.get('candidate_quotes', []))
            except Exception as e:
                logger.warning(f"  Error processing chunk {chunk_idx}: {e}")
        
        # Deduplicate quotes
        unique_quotes = list(dict.fromkeys(all_quotes))[:MAX_QUOTES_PER_THEME]
        
        return {
            "theme": theme,
            "review_count": len(reviews),
            "aggregated_key_points": all_key_points,
            "aggregated_candidate_quotes": unique_quotes
        }
    
    def run_reduce_stage(self, theme_summaries: List[Dict], date_range: Tuple[str, str]) -> Dict:
        """REDUCE stage: Create final weekly pulse note"""
        logger.info("REDUCE stage: Creating final weekly pulse")
        
        start_date, end_date = date_range
        themes_json = json.dumps(theme_summaries, indent=2)
        
        # Create REDUCE prompt
        reduce_prompt = REDUCE_PROMPT_TEMPLATE.format(
            start_date=start_date,
            end_date=end_date,
            themes_json=themes_json
        )
        
        try:
            # Call Gemini
            response = self.model.generate_content(reduce_prompt)
            response_text = response.text.strip()
            
            # Extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                return result
        except Exception as e:
            logger.error(f"Error in REDUCE stage: {e}")
            return None
    
    def get_date_range(self, reviews: List[Dict]) -> Tuple[str, str]:
        """Extract date range from reviews"""
        dates = [r.get('date') for r in reviews if r.get('date')]
        if dates:
            dates.sort()
            return dates[0], dates[-1]
        return datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')
    
    def run(self, api_key: str = None) -> Tuple[List[Dict], Dict]:
        """Execute complete MAP-REDUCE pipeline"""
        logger.info("=" * 80)
        logger.info("Starting Weekly Pulse Generation")
        logger.info("=" * 80)
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        if not self.model:
            logger.error("Gemini API not configured. Set GEMINI_API_KEY environment variable.")
            return None, None
        
        # Load reviews
        reviews = self.load_classified_reviews()
        
        # Group by theme
        themed_reviews = self.group_by_theme(reviews)
        
        # Get top 3 themes
        top_themes = self.get_top_themes(themed_reviews)
        
        # MAP stage for each theme
        logger.info("\n=== MAP STAGE ===")
        theme_summaries = []
        for theme, theme_reviews in top_themes.items():
            summary = self.run_map_stage(theme, theme_reviews)
            theme_summaries.append(summary)
        
        # Get date range for naming files
        date_range = self.get_date_range(reviews)
        start_date, end_date = date_range
        start_date_fmt = start_date.replace('-', '')
        end_date_fmt = end_date.replace('-', '')
        
        # Generate dated filenames with start AND end dates
        theme_summaries_file = f"data/review_theme_summaries_{start_date_fmt}_{end_date_fmt}.json"
        pulse_note_file = f"data/review_pulse_{start_date_fmt}_{end_date_fmt}.json"
        
        # Save theme summaries
        with open(theme_summaries_file, 'w', encoding='utf-8') as f:
            json.dump(theme_summaries, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved theme summaries to {theme_summaries_file}")
        
        # REDUCE stage
        logger.info("\n=== REDUCE STAGE ===")
        pulse_result = self.run_reduce_stage(theme_summaries, date_range)
        
        # Save pulse note
        if pulse_result:
            with open(pulse_note_file, 'w', encoding='utf-8') as f:
                json.dump(pulse_result, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved pulse note to {pulse_note_file}")
            
            # Print summary
            logger.info("\n=== SUMMARY ===")
            logger.info(f"Weekly Pulse: {pulse_result.get('start_date')} to {pulse_result.get('end_date')}")
            logger.info(f"Top Themes: {len(pulse_result.get('top_themes', []))}")
            logger.info(f"Quotes Selected: {len(pulse_result.get('quotes', []))}")
            logger.info(f"Action Ideas: {len(pulse_result.get('action_ideas', []))}")
            
            # Print the note
            logger.info("\n=== GENERATED PULSE NOTE ===")
            logger.info(pulse_result.get('note_markdown', ''))
        
        logger.info("\n" + "=" * 80)
        logger.info("PULSE GENERATION COMPLETED")
        logger.info("=" * 80)
        
        return theme_summaries_file, pulse_note_file, pulse_result


def main():
    """Main entry point"""
    import os
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Pulse generation may fail.")
    
    generator = WeeklyPulseGenerator(api_key=api_key)
    theme_summaries_file, pulse_note_file, pulse_result = generator.run(api_key)
    
    if pulse_result:
        print("\nWeekly Pulse Generated Successfully!")
        print(f"  Theme Summaries: {theme_summaries_file}")
        print(f"  Pulse Note: {pulse_note_file}")
    else:
        print("Pulse generation failed. Check logs for details.")


if __name__ == "__main__":
    main()
