#!/usr/bin/env python3
"""
Seed script for subscription_plans table.
Safe to run multiple times — skips seeding if plans already exist.

Columns in Plan model: id, name, price, duration_days, created_at, updated_at
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.subscription_plan import Plan
from settings.pydantic_config import settings


def get_sync_db_uri() -> str:
    """Derive a synchronous DB URI from settings."""
    if settings.DEV_ENV == "production":
        uri = settings.DATABASE_URL
        # Convert async drivers to sync equivalents
        uri = uri.replace("postgresql+asyncpg://", "postgresql://")
        uri = uri.replace("sqlite+aiosqlite://", "sqlite://")
        return uri
    else:
        return "sqlite:///./test.db"


def seed():
    db_uri = get_sync_db_uri()
    print(f"Connecting to: {db_uri}")

    engine = create_engine(db_uri, echo=False)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()

    try:
        existing = db.query(Plan).count()
        if existing > 0:
            print(f"Plans already exist ({existing}), skipping seed.")
        else:
            # 'trial' plan is used by registration — must exist with name='trial'
            plans = [
                Plan(name="trial", price=0.0, duration_days=36500),
                Plan(name="Pro", price=19.99, duration_days=30),
                Plan(name="Enterprise", price=99.99, duration_days=30),
            ]
            db.add_all(plans)
            db.commit()
            print(f"Seeded {len(plans)} plans successfully.")

        print("\nPlans in database:")
        for p in db.query(Plan).all():
            print(f"  id={p.id}  name={p.name}  price={p.price}  duration_days={p.duration_days}")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
