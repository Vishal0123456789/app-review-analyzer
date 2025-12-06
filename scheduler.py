"""
Auto Scheduler Module
Handles periodic execution of the analysis orchestrator (Monday 8 AM by default)
Runs independently from the frontend-triggered analysis flow
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

class AnalysisScheduler:
    """Manages automatic periodic execution of the analysis pipeline"""
    
    def __init__(self, enabled: bool = True, schedule_day: str = "mon", schedule_hour: int = 8, 
                 schedule_minute: int = 0, timezone: str = "UTC"):
        """
        Initialize the scheduler
        
        Args:
            enabled: Whether scheduler is enabled
            schedule_day: Day of week (mon, tue, wed, thu, fri, sat, sun)
            schedule_hour: Hour of day (0-23)
            schedule_minute: Minute of hour (0-59)
            timezone: Timezone for scheduling
        """
        self.enabled = enabled
        self.schedule_day = schedule_day
        self.schedule_hour = schedule_hour
        self.schedule_minute = schedule_minute
        self.timezone = timezone
        self.scheduler = None
        self.is_running = False
        
        # Get project root
        self.project_root = Path(__file__).parent.parent
        
        logger.info(f"AnalysisScheduler initialized - Enabled: {enabled}, "
                   f"Schedule: {schedule_day} {schedule_hour:02d}:{schedule_minute:02d} {timezone}")
    
    def start(self):
        """Start the background scheduler"""
        if not self.enabled:
            logger.info("Scheduler is disabled via configuration")
            return
        
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            self.scheduler = BackgroundScheduler(timezone=self.timezone)
            
            # Add job to run every Monday at specified time
            self.scheduler.add_job(
                func=self._run_analysis,
                trigger=CronTrigger(
                    day_of_week=self.schedule_day,
                    hour=self.schedule_hour,
                    minute=self.schedule_minute,
                    timezone=self.timezone
                ),
                id='weekly_analysis',
                name='Weekly Product Pulse Analysis',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Scheduler started successfully - Next run: {self._get_next_run_time()}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the background scheduler"""
        if self.scheduler and self.is_running:
            try:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Scheduler stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
    
    def _run_analysis(self):
        """Execute the orchestrator for analysis"""
        execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[SCHEDULER] Starting automatic analysis execution at {execution_time}")
        
        try:
            # Get environment variables
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            
            if not gemini_api_key:
                logger.error("[SCHEDULER] GEMINI_API_KEY not set - analysis skipped")
                return
            
            # Default window days (7 days = 1 week)
            window_days = int(os.getenv('SCHEDULER_WINDOW_DAYS', '7'))
            
            # Run orchestrator
            orchestrator_path = self.project_root / 'orchestrator.py'
            
            if not orchestrator_path.exists():
                logger.error(f"[SCHEDULER] Orchestrator not found at {orchestrator_path}")
                return
            
            # Execute with subprocess
            logger.info(f"[SCHEDULER] Executing: python orchestrator.py --window-days {window_days}")
            result = subprocess.run(
                ['python', str(orchestrator_path), '--window-days', str(window_days)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("[SCHEDULER] Analysis completed successfully")
            else:
                logger.error(f"[SCHEDULER] Analysis failed with return code {result.returncode}")
                logger.error(f"[SCHEDULER] Error output: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error("[SCHEDULER] Analysis execution timeout (30 minutes)")
        except Exception as e:
            logger.error(f"[SCHEDULER] Error during analysis execution: {e}")
    
    def _get_next_run_time(self) -> str:
        """Get the next scheduled run time"""
        if not self.scheduler or not self.is_running:
            return "Not scheduled"
        
        job = self.scheduler.get_job('weekly_analysis')
        if job:
            next_run = job.next_run_time
            return next_run.strftime("%Y-%m-%d %H:%M:%S %Z") if next_run else "Not scheduled"
        return "Not scheduled"
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            "enabled": self.enabled,
            "running": self.is_running,
            "schedule": f"{self.schedule_day} {self.schedule_hour:02d}:{self.schedule_minute:02d}",
            "timezone": self.timezone,
            "next_run": self._get_next_run_time()
        }


def create_scheduler() -> AnalysisScheduler:
    """Factory function to create and configure scheduler from environment"""
    enabled = os.getenv('SCHEDULER_ENABLED', 'false').lower() == 'true'
    schedule_day = os.getenv('SCHEDULER_DAY', 'mon')  # mon, tue, wed, thu, fri, sat, sun
    schedule_hour = int(os.getenv('SCHEDULER_HOUR', '8'))  # 0-23
    schedule_minute = int(os.getenv('SCHEDULER_MINUTE', '0'))  # 0-59
    timezone = os.getenv('SCHEDULER_TIMEZONE', 'UTC')
    
    return AnalysisScheduler(
        enabled=enabled,
        schedule_day=schedule_day,
        schedule_hour=schedule_hour,
        schedule_minute=schedule_minute,
        timezone=timezone
    )
