from typing import Type, Any, Optional, Union
from sqlalchemy import select, func
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import BinaryExpression
from models import (
    user, project, project_member, project_invitation, notification,
    uploaded_file, report, notification_recipient, subscription,
    subscription_plan, big_data_result
)
from models.base_model import Base, BaseModel
from contextlib import contextmanager
from settings.pydantic_config import settings

# ----------------- Engine & Session -----------------

_db_url = settings.DATABASE_URL
if "+asyncpg" in _db_url:
    SYNC_DATABASE_URL = _db_url.replace("+asyncpg", "+psycopg2")
elif _db_url.startswith("postgresql://") or _db_url.startswith("postgres://"):
    SYNC_DATABASE_URL = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
else:
    SYNC_DATABASE_URL = _db_url
# Validate the driver is sync-compatible
if "asyncpg" in SYNC_DATABASE_URL:
    raise ValueError(f"SYNC_DATABASE_URL still contains async driver: {SYNC_DATABASE_URL}")

engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Optional base
BaseSync = declarative_base()


# ----------------- Sync DB Storage -----------------

class SyncDBStorage:
    """Sync DB storage class for Celery tasks"""

    MODELS = {
        'User': user.User,
        'Project': project.Project,
        'ProjectMember': project_member.ProjectMember,
        'ProjectInvitation': project_invitation.ProjectInvitation,
        'Notification': notification.Notification,
        'UploadedFile': uploaded_file.UploadedFile,
        'Report': report.Report,
        'NotificationRecipient': notification_recipient.NotificationRecipient,
        'Subscription': subscription.Subscription,
        'Plan': subscription_plan.Plan,
        'BigDataResult': big_data_result.BigDataResult,
    }

    def __init__(self):
        self.engine = engine
        self.session_maker = SessionLocal

    @contextmanager
    def get_session(self) -> Session:
        """Sync session context manager"""
        session = self.session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ----------------- CRUD Methods -----------------

    def new(self, session: Session, obj: Type[Base]):
        session.add(obj)

    def add_all(self, session: Session, data: list[Type[Base]]):
        session.add_all(data)

    def save(self, session: Session):
        session.commit()

    def rollback(self, session: Session):
        session.rollback()

    def delete(self, session: Session, obj: Type[Base]):
        session.delete(obj)
        session.commit()

    def find_by(self, session: Session, cls: Type[Base], **kwargs: Any):
        result = session.execute(select(cls).filter_by(**kwargs))
        return result.scalars().first()

    def filter(self, session: Session, cls: Type[Base], *args: BinaryExpression, fetch_one: bool = False) -> Union[Base, list[Base], None]:
        result = session.execute(select(cls).filter(*args))
        if fetch_one:
            return result.scalars().first()
        return list(result.scalars().all())

    def all(self, session: Session, cls: Optional[Type[Base]] = None) -> dict:
        objects = {}
        if cls:
            result = session.execute(select(cls))
            for obj in list(result.scalars().all()):
                objects[f"{type(obj).__name__}.{obj.id}"] = obj
        else:
            for model in self.MODELS.values():
                result = session.execute(select(model))
                for obj in list(result.scalars().all()):
                    objects[f"{type(obj).__name__}.{obj.id}"] = obj
        return objects

    def get(self, session: Session, cls: Type[Union[Base, BaseModel]], obj_id: str) -> Optional[Union[Base, BaseModel]]:
        if cls and obj_id:
            result = session.execute(select(cls).filter(cls.id == obj_id))
            return result.scalar_one_or_none()
        return None

    def count(self, session: Session, cls: Optional[Type[Base]] = None) -> int:
        return len(self.all(session, cls))

    # ----------------- Join & Group Methods -----------------

    def filter_join(
        self,
        session: Session,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        *filters: BinaryExpression,
    ) -> list[Base]:
        stmt = select(primary_cls).join(
            join_cls, join_condition).where(*filters)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def filter_join_pair(
        self,
        session: Session,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        *filters: BinaryExpression,
    ) -> list:
        stmt = select(primary_cls, join_cls).join(
            join_cls, join_condition).where(*filters)
        result = session.execute(stmt)
        return list(result.all())

    def count_grouped_join(
        self,
        session: Session,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        group_by_col: Any,
        *filters: BinaryExpression,
    ) -> list:
        stmt = select(group_by_col, func.count(primary_cls.id)) \
            .join(join_cls, join_condition) \
            .where(*filters) \
            .group_by(group_by_col)
        result = session.execute(stmt)
        return list(result.all())

    def count_where(self, session: Session, cls: Type[Base], *filters: BinaryExpression) -> int:
        stmt = select(func.count()).select_from(cls).where(*filters)
        result = session.execute(stmt)
        return result.scalar_one()
