"""
Background scheduler — runs ScholarshipSync every N hours.
"""
import threading
import time
import logging
from datetime import datetime
from database import db
from services.scholarship_sync import ScholarshipSync

logger = logging.getLogger(__name__)

_scheduler_thread = None
_stop_event = threading.Event()


def _run_sync():
    try:
        logger.info(f"[Scheduler] Sync tick at {datetime.utcnow().isoformat()}")
        sync = ScholarshipSync(db=db)
        stats = sync.run()
        logger.info(f"[Scheduler] Done: saved={stats['saved']}, db_total={stats['db_total']}")
    except Exception as e:
        logger.error(f"[Scheduler] Error: {e}")


def _scheduler_loop(interval_hours):
    _run_sync()  # run once immediately
    while not _stop_event.is_set():
        # Sleep in 60s chunks so we can stop quickly
        for _ in range(int(interval_hours * 3600 / 60)):
            if _stop_event.is_set():
                return
            time.sleep(60)
        _run_sync()


def start_scheduler(interval_hours=24):
    """Start background scheduler thread."""
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.info("[Scheduler] Already running")
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        args=(interval_hours,),
        daemon=True
    )
    _scheduler_thread.start()
    logger.info(f"[Scheduler] Started (every {interval_hours}h)")


def stop_scheduler():
    _stop_event.set()
    logger.info("[Scheduler] Stopped")