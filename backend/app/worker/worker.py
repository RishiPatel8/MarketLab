import time
import logging
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import SyncSessionLocal
from app.db.models.research_run import ResearchRun
from app.worker.tasks import execute_research_workflow

logger = logging.getLogger("marketlab.standalone_worker")

def run_worker_loop():
    """
    Continuous background worker process that polls for queued research runs
    when running as a dedicated container or daemon.
    """
    setup_logging()
    logger.info("MarketLab AI Background Worker started. Waiting for jobs...")

    while True:
        try:
            with SyncSessionLocal() as db:
                queued_run = db.query(ResearchRun).filter(ResearchRun.status == "queued").order_by(ResearchRun.created_at.asc()).first()
                if queued_run:
                    run_id = queued_run.id
                else:
                    run_id = None

            if run_id:
                logger.info(f"Picked up queued research run: {run_id}")
                execute_research_workflow(run_id)
            else:
                time.sleep(2)
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker_loop()
