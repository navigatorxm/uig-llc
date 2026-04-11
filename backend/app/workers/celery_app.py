from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "uig_pipeline",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.scraping_tasks",
        "app.workers.outreach_tasks",
        "app.workers.verification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Periodic tasks (beat schedule)
celery_app.conf.beat_schedule = {
    # Daily scraping job at 8am IST
    "daily-scrape-delhi-buy": {
        "task": "app.workers.scraping_tasks.scrape_portal",
        "schedule": crontab(hour=8, minute=0),
        "args": ("99acres", "Delhi NCR", "buy", None, 10),
    },
    "daily-scrape-delhi-rent": {
        "task": "app.workers.scraping_tasks.scrape_portal",
        "schedule": crontab(hour=8, minute=30),
        "args": ("magicbricks", "Delhi NCR", "rent", None, 10),
    },
    # Follow-up check every 2 hours (catches 8h/16h/24h/36h/48h windows accurately)
    "check-follow-ups": {
        "task": "app.workers.outreach_tasks.process_follow_ups",
        "schedule": crontab(hour="*/2"),
    },
}
