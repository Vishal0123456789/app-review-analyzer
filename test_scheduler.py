"""
Scheduler Testing Script
Quick tests for the auto-scheduler module
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from layer4_email.scheduler import AnalysisScheduler, create_scheduler


class TestSchedulerInitialization:
    """Test scheduler initialization"""
    
    def test_scheduler_init_defaults(self):
        """Test scheduler initializes with defaults"""
        scheduler = AnalysisScheduler()
        
        assert scheduler.enabled == True
        assert scheduler.schedule_day == "mon"
        assert scheduler.schedule_hour == 8
        assert scheduler.schedule_minute == 0
        assert scheduler.timezone == "UTC"
        assert scheduler.is_running == False
    
    def test_scheduler_init_custom(self):
        """Test scheduler initializes with custom parameters"""
        scheduler = AnalysisScheduler(
            enabled=True,
            schedule_day="fri",
            schedule_hour=18,
            schedule_minute=30,
            timezone="Asia/Kolkata"
        )
        
        assert scheduler.enabled == True
        assert scheduler.schedule_day == "fri"
        assert scheduler.schedule_hour == 18
        assert scheduler.schedule_minute == 30
        assert scheduler.timezone == "Asia/Kolkata"
    
    def test_scheduler_disabled(self):
        """Test scheduler respects disabled flag"""
        scheduler = AnalysisScheduler(enabled=False)
        
        assert scheduler.enabled == False
        assert scheduler.is_running == False


class TestSchedulerStatus:
    """Test scheduler status reporting"""
    
    def test_get_status_enabled(self):
        """Test get_status returns correct format when enabled"""
        scheduler = AnalysisScheduler(enabled=True)
        status = scheduler.get_status()
        
        assert isinstance(status, dict)
        assert "enabled" in status
        assert "running" in status
        assert "schedule" in status
        assert "timezone" in status
        assert "next_run" in status
        
        assert status["enabled"] == True
        assert status["running"] == False  # Not started yet
    
    def test_get_status_disabled(self):
        """Test get_status returns correct format when disabled"""
        scheduler = AnalysisScheduler(enabled=False)
        status = scheduler.get_status()
        
        assert status["enabled"] == False
        assert status["running"] == False
        assert status["next_run"] == "Not scheduled"


class TestSchedulerLifecycle:
    """Test scheduler start/stop lifecycle"""
    
    def test_scheduler_start_stop(self):
        """Test scheduler start and stop"""
        scheduler = AnalysisScheduler(enabled=True)
        
        # Start
        scheduler.start()
        assert scheduler.is_running == True
        assert scheduler.scheduler is not None
        
        # Stop
        scheduler.stop()
        assert scheduler.is_running == False
    
    def test_scheduler_start_when_disabled(self):
        """Test start is no-op when disabled"""
        scheduler = AnalysisScheduler(enabled=False)
        scheduler.start()
        
        assert scheduler.is_running == False
        assert scheduler.scheduler is None
    
    def test_scheduler_double_start(self):
        """Test starting already running scheduler doesn't error"""
        scheduler = AnalysisScheduler(enabled=True)
        
        scheduler.start()
        first_run = scheduler.is_running
        
        # Start again - should be no-op
        scheduler.start()
        assert scheduler.is_running == first_run
        
        # Cleanup
        scheduler.stop()


class TestSchedulerFactory:
    """Test environment-based factory function"""
    
    def test_factory_creates_scheduler(self):
        """Test factory creates scheduler instance"""
        os.environ['SCHEDULER_ENABLED'] = 'false'
        scheduler = create_scheduler()
        
        assert isinstance(scheduler, AnalysisScheduler)
    
    def test_factory_reads_enabled_env(self):
        """Test factory reads SCHEDULER_ENABLED"""
        os.environ['SCHEDULER_ENABLED'] = 'true'
        scheduler = create_scheduler()
        assert scheduler.enabled == True
        
        os.environ['SCHEDULER_ENABLED'] = 'false'
        scheduler = create_scheduler()
        assert scheduler.enabled == False
    
    def test_factory_reads_day_env(self):
        """Test factory reads SCHEDULER_DAY"""
        os.environ['SCHEDULER_DAY'] = 'fri'
        scheduler = create_scheduler()
        assert scheduler.schedule_day == 'fri'
    
    def test_factory_reads_hour_env(self):
        """Test factory reads SCHEDULER_HOUR"""
        os.environ['SCHEDULER_HOUR'] = '18'
        scheduler = create_scheduler()
        assert scheduler.schedule_hour == 18
    
    def test_factory_reads_minute_env(self):
        """Test factory reads SCHEDULER_MINUTE"""
        os.environ['SCHEDULER_MINUTE'] = '30'
        scheduler = create_scheduler()
        assert scheduler.schedule_minute == 30
    
    def test_factory_reads_timezone_env(self):
        """Test factory reads SCHEDULER_TIMEZONE"""
        os.environ['SCHEDULER_TIMEZONE'] = 'Asia/Kolkata'
        scheduler = create_scheduler()
        assert scheduler.timezone == 'Asia/Kolkata'
    
    def test_factory_defaults(self):
        """Test factory uses defaults when env not set"""
        # Clear env vars
        for key in ['SCHEDULER_ENABLED', 'SCHEDULER_DAY', 'SCHEDULER_HOUR', 
                    'SCHEDULER_MINUTE', 'SCHEDULER_TIMEZONE']:
            os.environ.pop(key, None)
        
        scheduler = create_scheduler()
        
        assert scheduler.enabled == False  # Default is disabled
        assert scheduler.schedule_day == 'mon'
        assert scheduler.schedule_hour == 8
        assert scheduler.schedule_minute == 0
        assert scheduler.timezone == 'UTC'


class TestSchedulerConfiguration:
    """Test scheduler configuration variations"""
    
    def test_all_days_of_week(self):
        """Test all days of week can be configured"""
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        
        for day in days:
            scheduler = AnalysisScheduler(schedule_day=day)
            assert scheduler.schedule_day == day
    
    def test_all_hours(self):
        """Test all valid hours can be configured"""
        for hour in [0, 6, 12, 18, 23]:
            scheduler = AnalysisScheduler(schedule_hour=hour)
            assert scheduler.schedule_hour == hour
    
    def test_all_minutes(self):
        """Test all valid minutes can be configured"""
        for minute in [0, 15, 30, 45, 59]:
            scheduler = AnalysisScheduler(schedule_minute=minute)
            assert scheduler.schedule_minute == minute
    
    def test_common_timezones(self):
        """Test common timezones can be configured"""
        timezones = [
            'UTC',
            'America/New_York',
            'Europe/London',
            'Asia/Kolkata',
            'Asia/Tokyo'
        ]
        
        for tz in timezones:
            try:
                scheduler = AnalysisScheduler(timezone=tz)
                assert scheduler.timezone == tz
            except Exception as e:
                # Some timezones might not be available on system
                print(f"Warning: Timezone {tz} not available: {e}")


class TestSchedulerStatus:
    """Test scheduler status formatting"""
    
    def test_status_format_schedule(self):
        """Test schedule format in status"""
        scheduler = AnalysisScheduler(
            schedule_day="fri",
            schedule_hour=18,
            schedule_minute=30
        )
        status = scheduler.get_status()
        
        assert status["schedule"] == "fri 18:30"
    
    def test_status_format_different_times(self):
        """Test schedule format with different times"""
        test_cases = [
            {"hour": 8, "minute": 0, "expected": "mon 08:00"},
            {"hour": 18, "minute": 30, "expected": "mon 18:30"},
            {"hour": 0, "minute": 0, "expected": "mon 00:00"},
            {"hour": 23, "minute": 59, "expected": "mon 23:59"},
        ]
        
        for case in test_cases:
            scheduler = AnalysisScheduler(
                schedule_hour=case["hour"],
                schedule_minute=case["minute"]
            )
            status = scheduler.get_status()
            assert case["expected"] in status["schedule"]


def test_scheduler_project_root():
    """Test scheduler correctly identifies project root"""
    scheduler = AnalysisScheduler()
    assert scheduler.project_root.exists()
    assert (scheduler.project_root / "orchestrator.py").exists()


# Run tests with: pytest test_scheduler.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
