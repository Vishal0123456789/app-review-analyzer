"""
Orchestrator: Weekly App Review Pulse Workflow
Coordinates Layer 1 (Scraping) → Layer 2 (Classification) → Layer 3 (Insights) → Layer 4 (Email)
Safe for weekly cron scheduling.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple
import sys

# Add layer directories to path
sys.path.insert(0, str(Path(__file__).parent / "layer1_scraping"))
sys.path.insert(0, str(Path(__file__).parent / "layer2_classification"))
sys.path.insert(0, str(Path(__file__).parent / "layer3_insights"))
sys.path.insert(0, str(Path(__file__).parent / "layer4_email"))

from layer1_scraping.scheduler_runner import ReviewScheduler
from layer2_classification.review_classifier import ReviewClassifier
from layer3_insights.weekly_pulse_generator import WeeklyPulseGenerator
from layer4_email.email_pulse_sender import EmailPulseSender

# Setup logging
log_date = datetime.now().strftime('%Y%m%d')
os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/orchestrator_{log_date}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeeklyPulseOrchestrator:
    """Orchestrates the complete weekly review pulse workflow"""
    
    def __init__(self, api_key: str = None, window_days: int = 28):
        """Initialize orchestrator
        
        Args:
            api_key: Gemini API key (optional, can use env var)
            window_days: Number of days to look back (default 28)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.window_days = window_days
        self.workflow_summary = {}
        logger.info("WeeklyPulseOrchestrator initialized")
    
    def calculate_date_window(self) -> Tuple[str, str]:
        """Calculate the date window for scraping
        
        Returns:
            Tuple of (START_DATE, END_DATE) in YYYY-MM-DD format
        """
        today = datetime.now().date()
        end_date = today
        start_date = today - timedelta(days=self.window_days - 1)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Date window: {start_date_str} to {end_date_str} ({self.window_days} days)")
        return start_date_str, end_date_str
    
    def run_layer1_scraping(self, start_date: str, end_date: str) -> Tuple[bool, str, str, str]:
        """Execute Layer 1: Data Scraping & Storage
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Tuple of (success, json_file, csv_file, error_msg)
        """
        logger.info("=" * 80)
        logger.info("LAYER 1: DATA SCRAPING & STORAGE")
        logger.info("=" * 80)
        
        try:
            scheduler = ReviewScheduler(start_date=start_date, end_date=end_date)
            report, json_file, csv_file = scheduler.run_extraction()
            
            if report:
                logger.info("[OK] Layer 1 completed successfully")
                logger.info(f"  Output JSON: {json_file}")
                logger.info(f"  Output CSV: {csv_file}")
                return True, json_file, csv_file, None
            else:
                error_msg = "Layer 1 returned no report"
                logger.error(f"[FAIL] Layer 1 failed: {error_msg}")
                return False, None, None, error_msg
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[FAIL] Layer 1 exception: {error_msg}")
            return False, None, None, error_msg
    
    def run_layer2_classification(self, input_json: str) -> Tuple[bool, str, str, str]:
        """Execute Layer 2: Classification & Analysis
        
        Args:
            input_json: Path to input JSON file from Layer 1
        
        Returns:
            Tuple of (success, json_file, csv_file, error_msg)
        """
        logger.info("\n" + "=" * 80)
        logger.info("LAYER 2: CLASSIFICATION & ANALYSIS")
        logger.info("=" * 80)
        
        try:
            # Resolve the input path
            if not Path(input_json).is_absolute():
                input_json_path = Path.cwd() / input_json
            else:
                input_json_path = Path(input_json)
            
            # Check if file exists, if not try with data/ prefix
            if not input_json_path.exists():
                input_json_path = Path.cwd() / "data" / Path(input_json).name
            
            if not input_json_path.exists():
                error_msg = f"Input file not found: {input_json}"
                logger.error(f"[FAIL] Layer 2 failed: {error_msg}")
                return False, None, None, error_msg
            
            # Update classifier input file
            from layer2_classification import classify_config
            classify_config.INPUT_FILE = str(input_json_path)
            
            classifier = ReviewClassifier(api_key=self.api_key)
            summary = classifier.run(self.api_key, input_file=str(input_json_path))
            
            if summary:
                logger.info("[OK] Layer 2 completed successfully")
                logger.info(f"  Total reviews classified: {summary['total_classified']}")
                logger.info(f"  Output JSON: {summary['json_output']}")
                logger.info(f"  Output CSV: {summary['csv_output']}")
                return True, summary['json_output'], summary['csv_output'], None
            else:
                error_msg = "Layer 2 returned no summary"
                logger.error(f"[FAIL] Layer 2 failed: {error_msg}")
                return False, None, None, error_msg
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[FAIL] Layer 2 exception: {error_msg}")
            return False, None, None, error_msg
    
    def run_layer3_insights(self, input_json: str, target_week_end: str) -> Tuple[bool, str, str, str]:
        """Execute Layer 3: Insights & Weekly Pulse
        
        Args:
            input_json: Path to input JSON file from Layer 2
            target_week_end: End date of the week (for naming outputs)
        
        Returns:
            Tuple of (success, theme_summaries_file, pulse_file, error_msg)
        """
        logger.info("\n" + "=" * 80)
        logger.info("LAYER 3: INSIGHTS & WEEKLY PULSE")
        logger.info("=" * 80)
        
        try:
            # Resolve the input path
            if not Path(input_json).is_absolute():
                input_json_path = Path.cwd() / input_json
            else:
                input_json_path = Path(input_json)
            
            # Check if file exists, if not try with data/ prefix
            if not input_json_path.exists():
                input_json_path = Path.cwd() / "data" / Path(input_json).name
            
            if not input_json_path.exists():
                error_msg = f"Input file not found: {input_json}"
                logger.error(f"[FAIL] Layer 3 failed: {error_msg}")
                return False, None, None, error_msg
            
            # Update insights input file
            from layer3_insights import insights_config
            insights_config.INPUT_FILE = str(input_json_path)
            
            generator = WeeklyPulseGenerator(api_key=self.api_key, input_file=str(input_json_path))
            theme_summaries_file, pulse_file, pulse_result = generator.run(self.api_key)
            
            if pulse_result:
                logger.info("[OK] Layer 3 completed successfully")
                logger.info(f"  Theme Summaries: {theme_summaries_file}")
                logger.info(f"  Pulse Note: {pulse_file}")
                return True, theme_summaries_file, pulse_file, None
            else:
                error_msg = "Layer 3 returned no pulse result"
                logger.error(f"[FAIL] Layer 3 failed: {error_msg}")
                return False, None, None, error_msg
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[FAIL] Layer 3 exception: {error_msg}")
            return False, None, None, error_msg
    
    def run_layer4_email(self, pulse_json: str) -> Tuple[bool, str, str, str]:
        """Execute Layer 4: Email & Communication
        
        Args:
            pulse_json: Path to pulse JSON file from Layer 3
        
        Returns:
            Tuple of (success, subject_line, send_log_file, error_msg)
        """
        logger.info("\n" + "=" * 80)
        logger.info("LAYER 4: EMAIL & COMMUNICATION")
        logger.info("=" * 80)
        
        try:
            # Resolve the input path
            if not Path(pulse_json).is_absolute():
                pulse_json_path = Path.cwd() / pulse_json
            else:
                pulse_json_path = Path(pulse_json)
            
            # Check if file exists, if not try with data/ prefix
            if not pulse_json_path.exists():
                pulse_json_path = Path.cwd() / "data" / Path(pulse_json).name
            
            if not pulse_json_path.exists():
                error_msg = f"Input file not found: {pulse_json}"
                logger.error(f"[FAIL] Layer 4 failed: {error_msg}")
                return False, None, None, error_msg
            
            # Update email input file
            from layer4_email import email_config
            email_config.INPUT_PULSE_FILE = str(pulse_json_path)
            
            sender = EmailPulseSender(api_key=self.api_key, pulse_file=str(pulse_json_path))
            subject, body, log_file, status = sender.run(self.api_key)
            
            if subject and body:
                logger.info(f"[OK] Layer 4 completed successfully")
                logger.info(f"  Subject: {subject}")
                logger.info(f"  Body length: {len(body)} characters")
                logger.info(f"  Send log: {log_file}")
                logger.info(f"  Status: {status}")
                return True, subject, log_file, None
            else:
                error_msg = "Layer 4 failed to generate email"
                logger.error(f"[FAIL] Layer 4 failed: {error_msg}")
                return False, None, None, error_msg
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[FAIL] Layer 4 exception: {error_msg}")
            return False, None, None, error_msg
    
    def save_workflow_summary(self, summary: Dict) -> str:
        """Save workflow summary to JSON file
        
        Args:
            summary: Workflow summary dictionary
        
        Returns:
            Path to saved summary file
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = f"data/workflow_summary_{timestamp}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Workflow summary saved to {log_file}")
        return log_file
    
    def run(self) -> Dict:
        """Execute the complete weekly pulse workflow
        
        Returns:
            Dictionary with workflow status and details
        """
        logger.info("\n" + "=" * 80)
        logger.info("STARTING WEEKLY APP REVIEW PULSE WORKFLOW")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # Step 1: Calculate date window
        start_date, end_date = self.calculate_date_window()
        
        # Initialize summary
        summary = {
            "start_date": start_date,
            "end_date": end_date,
            "status": "error",
            "failed_layer": None,
            "details": "",
            "timestamps": {
                "workflow_start": start_time.isoformat(),
                "layer1_start": None,
                "layer1_end": None,
                "layer2_start": None,
                "layer2_end": None,
                "layer3_start": None,
                "layer3_end": None,
                "layer4_start": None,
                "layer4_end": None
            },
            "outputs": {
                "layer1_json": None,
                "layer1_csv": None,
                "layer2_json": None,
                "layer2_csv": None,
                "layer3_themes": None,
                "layer3_pulse": None,
                "layer4_subject": None,
                "layer4_log": None
            }
        }
        
        # Step 2: Layer 1 - Scraping
        logger.info(f"\nExecuting Layer 1...")
        summary["timestamps"]["layer1_start"] = datetime.now().isoformat()
        success, json_file, csv_file, error_msg = self.run_layer1_scraping(start_date, end_date)
        summary["timestamps"]["layer1_end"] = datetime.now().isoformat()
        
        if not success:
            summary["failed_layer"] = "layer1_scraping"
            summary["details"] = error_msg
            logger.error("[FAIL] Workflow stopped at Layer 1")
            self.save_workflow_summary(summary)
            return summary
        
        summary["outputs"]["layer1_json"] = json_file
        summary["outputs"]["layer1_csv"] = csv_file
        
        # Step 3: Layer 2 - Classification
        logger.info(f"\nExecuting Layer 2...")
        summary["timestamps"]["layer2_start"] = datetime.now().isoformat()
        success, json_file2, csv_file2, error_msg = self.run_layer2_classification(json_file)
        summary["timestamps"]["layer2_end"] = datetime.now().isoformat()
        
        if not success:
            summary["failed_layer"] = "layer2_classification"
            summary["details"] = error_msg
            logger.error("[FAIL] Workflow stopped at Layer 2")
            self.save_workflow_summary(summary)
            return summary
        
        summary["outputs"]["layer2_json"] = json_file2
        summary["outputs"]["layer2_csv"] = csv_file2
        
        # Step 4: Layer 3 - Insights
        logger.info(f"\nExecuting Layer 3...")
        summary["timestamps"]["layer3_start"] = datetime.now().isoformat()
        success, themes_file, pulse_file, error_msg = self.run_layer3_insights(json_file2, end_date)
        summary["timestamps"]["layer3_end"] = datetime.now().isoformat()
        
        if not success:
            summary["failed_layer"] = "layer3_insights"
            summary["details"] = error_msg
            logger.error("[FAIL] Workflow stopped at Layer 3")
            self.save_workflow_summary(summary)
            return summary
        
        summary["outputs"]["layer3_themes"] = themes_file
        summary["outputs"]["layer3_pulse"] = pulse_file
        
        # Step 5: Layer 4 - Email
        logger.info(f"\nExecuting Layer 4...")
        summary["timestamps"]["layer4_start"] = datetime.now().isoformat()
        success, subject, log_file, error_msg = self.run_layer4_email(pulse_file)
        summary["timestamps"]["layer4_end"] = datetime.now().isoformat()
        
        if not success:
            summary["failed_layer"] = "layer4_email"
            summary["details"] = error_msg
            logger.error("[FAIL] Workflow stopped at Layer 4")
            self.save_workflow_summary(summary)
            return summary
        
        summary["outputs"]["layer4_subject"] = subject
        summary["outputs"]["layer4_log"] = log_file
        
        # All layers completed successfully
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary["status"] = "success"
        summary["details"] = f"All 4 layers completed successfully in {duration:.2f} seconds"
        summary["timestamps"]["workflow_end"] = end_time.isoformat()
        
        logger.info("\n" + "=" * 80)
        logger.info("[OK] WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info(f"Date window: {start_date} to {end_date}")
        
        # Save summary
        summary["summary_file"] = self.save_workflow_summary(summary)
        
        return summary


def run_weekly_pulse(api_key: str = None, window_days: int = 28) -> Dict:
    """
    Main entry point for weekly pulse workflow
    
    Args:
        api_key: Gemini API key (optional, can use GEMINI_API_KEY env var)
        window_days: Number of days to look back (default 28)
    
    Returns:
        Workflow summary dictionary
    """
    orchestrator = WeeklyPulseOrchestrator(api_key=api_key, window_days=window_days)
    return orchestrator.run()


def main():
    """CLI entry point"""
    import argparse
    import sys
    
    # ... existing code ...
    
    # Enable UTF-8 output on Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(
        description="Weekly App Review Pulse Orchestrator"
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=28,
        help="Number of days to look back (default 28)"
    )
    
    args = parser.parse_args()
    
    # Run workflow
    summary = run_weekly_pulse(window_days=args.window_days)
    
    # Print summary
    print("\n" + "=" * 80)
    print("WORKFLOW SUMMARY")
    print("=" * 80)
    print(f"Status: {summary['status'].upper()}")
    print(f"Date window: {summary['start_date']} to {summary['end_date']}")
    
    if summary['status'] == 'success':
        print(f"Details: {summary['details']}")
        print(f"\nGenerated outputs:")
        print(f"  Layer 1 JSON: {summary['outputs']['layer1_json']}")
        print(f"  Layer 2 JSON: {summary['outputs']['layer2_json']}")
        print(f"  Layer 3 Pulse: {summary['outputs']['layer3_pulse']}")
        # Handle emoji in subject line safely
        try:
            subject = summary['outputs']['layer4_subject']
            print(f"  Layer 4 Email Subject: {subject}")
        except UnicodeEncodeError:
            # Fallback if emoji can't be encoded
            subject = summary['outputs']['layer4_subject'].encode('utf-8', 'replace').decode('utf-8')
            print(f"  Layer 4 Email Subject: {subject}")
        print(f"\nSummary saved to: {summary['summary_file']}")
    else:
        print(f"Failed at: {summary['failed_layer']}")
        print(f"Error: {summary['details']}")
    
    print("=" * 80 + "\n")
    
    return 0 if summary['status'] == 'success' else 1


if __name__ == "__main__":
    exit(main())
