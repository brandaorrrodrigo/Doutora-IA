"""
Background worker for Doutora IA
Handles: PDF generation, data ingestion, cleanup tasks
"""
import os
import sys
import time
import redis
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/doutora")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL)


def process_report_generation(task_data: dict):
    """Process report generation task"""
    case_id = task_data.get("case_id")

    print(f"Generating report for case {case_id}...")

    # Import here to avoid circular imports
    from api.services.pdf import generate_pdf_report
    from api.models import Case

    db = SessionLocal()

    try:
        case = db.query(Case).filter(Case.id == case_id).first()

        if not case:
            print(f"Case {case_id} not found")
            return

        # Generate report
        report_path = generate_pdf_report(case, os.getenv("CORPUS_UPDATE_DATE", "09/12/2025"))

        # Update case
        case.report_url = f"/reports/{os.path.basename(report_path)}"
        db.commit()

        print(f"✓ Report generated: {report_path}")

    except Exception as e:
        print(f"✗ Error generating report: {e}")
        db.rollback()

    finally:
        db.close()


def process_data_ingestion(task_data: dict):
    """Process data ingestion task"""
    json_dir = task_data.get("json_dir")

    print(f"Ingesting data from {json_dir}...")

    # Import ingest functions
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ingest"))
    from build_corpus import load_json_documents, ingest_to_qdrant

    try:
        docs = load_json_documents(json_dir)
        ingest_to_qdrant(docs)
        print("✓ Data ingestion completed")

    except Exception as e:
        print(f"✗ Error ingesting data: {e}")


def process_cleanup(task_data: dict):
    """Process cleanup task (old reports, expired referrals, etc)"""
    print("Running cleanup tasks...")

    from api.models import Referral, ReferralStatus

    db = SessionLocal()

    try:
        # Expire old referrals
        expired = db.query(Referral).filter(
            Referral.status == ReferralStatus.PENDING,
            Referral.expires_at < datetime.utcnow()
        ).all()

        for ref in expired:
            ref.status = ReferralStatus.EXPIRED

        db.commit()

        print(f"✓ Expired {len(expired)} referrals")

        # Clean up old report files (older than 30 days)
        reports_dir = "/reports"
        if os.path.exists(reports_dir):
            cutoff_time = time.time() - (30 * 24 * 60 * 60)
            cleaned = 0

            for filename in os.listdir(reports_dir):
                filepath = os.path.join(reports_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        cleaned += 1

            print(f"✓ Cleaned {cleaned} old report files")

    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        db.rollback()

    finally:
        db.close()


def process_task(task_type: str, task_data: dict):
    """Process a task based on its type"""
    if task_type == "generate_report":
        process_report_generation(task_data)

    elif task_type == "ingest_data":
        process_data_ingestion(task_data)

    elif task_type == "cleanup":
        process_cleanup(task_data)

    else:
        print(f"Unknown task type: {task_type}")


def worker_loop():
    """Main worker loop"""
    print("Worker started, waiting for tasks...")

    while True:
        try:
            # Blocking pop from Redis queue (timeout 5 seconds)
            result = redis_client.blpop("tasks", timeout=5)

            if result:
                queue_name, task_json = result
                task = json.loads(task_json)

                task_type = task.get("type")
                task_data = task.get("data", {})

                print(f"\n>>> Processing task: {task_type}")
                process_task(task_type, task_data)

            else:
                # No tasks, run periodic cleanup
                # Every hour
                if int(time.time()) % 3600 < 5:
                    process_task("cleanup", {})

        except KeyboardInterrupt:
            print("\nWorker stopped by user")
            break

        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    worker_loop()
