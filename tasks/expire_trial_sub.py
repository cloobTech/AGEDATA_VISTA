from sqlalchemy import select
from storage.celery_db import SessionLocal
from datetime import datetime, timezone
from celery_app import celery_app
from models.subscription import Subscription
from models.subscription_plan import Plan


@celery_app.task(bind=True, name="expire_subscriptions")
def expire_trials(self):
    with SessionLocal() as session:

        try:
            now = datetime.now(timezone.utc)

            stmt = (
                select(Subscription)
                .join(Subscription.subscription_plan)
                .where(
                    Plan.name == "trial",
                    Subscription.end_date <= now,
                    Subscription.status == "active",
                )
            )

            result = session.execute(stmt)
            expired_trials = result.scalars().all()

            for trial in expired_trials:
                trial.status = "expired"

            session.commit()
        except Exception as exc:
            session.rollback()
            raise self.retry(exc=exc, countdown=30, max_retries=3)

        # expire them
        finally:
            session.close()


# FASTER QUERY FOR LARGE DATASET

# from sqlalchemy import update

# stmt = (
#     update(Subscription)
#     .where(
#         Subscription.plan_id == select(Plan.id).where(Plan.name == "trial").scalar_subquery(),
#         Subscription.end_date <= now,
#         Subscription.is_active.is_(True)
#     )
#     .values(is_active=False)
# )

# db.execute(stmt)
# db.commit()
