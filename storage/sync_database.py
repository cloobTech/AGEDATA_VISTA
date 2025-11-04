# storage/database_sync.py
from typing import Type, Any, Optional, Union, Generator
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import user, project, project_member, project_invitation, notification, uploaded_file, report, notification_recipient, subscription, subscription_plan, big_data_result
from models.base_model import Base, BaseModel
from sqlalchemy.sql import Select
from contextlib import contextmanager


class DBSyncStorage:
    """Synchronous database storage class for Celery tasks and sync operations"""

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

    __engine = None
    __session_maker = None

    def __init__(self, db_uri: str):
        """Initialize the sync database storage class"""
        self.__engine = create_engine(db_uri, echo=False, pool_pre_ping=True)
        self.__session_maker = sessionmaker(
            bind=self.__engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Create and return a sync session object"""
        session = self.__session_maker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def reload(self):
        """Reload the database schema (sync)"""
        Base.metadata.create_all(self.__engine)

    def drop_all(self):
        """Drop all tables in the database (sync)"""
        Base.metadata.drop_all(self.__engine)

    def new(self, session: Session, obj: Type[Base]):
        """Add objects to the current database session"""
        session.add(obj)

    def add_all(self, session: Session, data: list[Type[Base]]):
        """Add Batch"""
        session.add_all(data)

    def save(self, session: Session):
        """Commit all changes of the current database session."""
        session.commit()

    def rollback(self, session: Session):
        """Roll back the current database session."""
        session.rollback()

    def delete(self, session: Session, obj: Type[Base]):
        """Delete an object from the current database session"""
        session.delete(obj)
        self.save(session)

    def find_by(self, session: Session, cls: Type[Base], **kwargs: Any) -> Type[Base] | None:
        """Retrieves one object based on a class name and kwargs (class attribute)"""
        query_result = session.execute(select(cls).filter_by(**kwargs))
        return query_result.scalars().first()

    def filter(self, session: Session, cls: Type[Base], *args: BinaryExpression, fetch_one: bool = False) -> Base | list[Base] | None:
        """Retrieve objects based on filters"""
        query_result = session.execute(select(cls).filter(*args))
        result = query_result.scalars()
        return result.first() if fetch_one else result.all()

    def all(self, session: Session, cls: Type[Base] | None = None) -> dict:
        """Query all objects of a specific class or all models."""
        objects = {}
        if cls is not None:
            result = session.execute(select(cls))
            result = result.scalars().all()
            for obj in result:
                obj_reference = f'{type(obj).__name__}.{obj.id}'
                objects[obj_reference] = obj
        else:
            for model in self.MODELS.values():
                result = session.execute(select(model))
                result = result.scalars().all()
                for obj in result:
                    obj_reference = f'{type(obj).__name__}.{obj.id}'
                    objects[obj_reference] = obj
        return objects

    def get(self, session: Session, cls: Type[Union[Base, BaseModel]], obj_id: str) -> Optional[Union[Base, BaseModel]]:
        """Retrieve a single object by its class and ID."""
        if cls and obj_id:
            result = session.execute(select(cls).filter(cls.id == obj_id))
            return result.scalar_one_or_none()
        return None

    def filter_join(
        self,
        session: Session,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        *filters: BinaryExpression,
    ) -> list[Base]:
        """Run a SELECT with JOIN and filters (sync)"""
        stmt: Select = (
            select(primary_cls)
            .join(join_cls, join_condition)
            .where(*filters)
        )
        result = session.execute(stmt)
        return result.scalars().all()

    def count(self, session: Session, cls: Type[Base] | None = None) -> int:
        """Return the count of all objects in storage"""
        objects = self.all(session, cls)
        return len(objects)

    def filter_join_pair(
        self,
        session: Session,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        *filters: BinaryExpression,
    ) -> list[tuple[Base, Base]]:
        """Run a SELECT with JOIN and return (A, B) tuples (sync)"""
        stmt = (
            select(primary_cls, join_cls)
            .join(join_cls, join_condition)
            .where(*filters)
        )
        result = session.execute(stmt)
        return result.all()

    def count_grouped_join(
        self,
        session: Session,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        group_by_col: Any,
        *filters: BinaryExpression,
    ) -> list[tuple[Any, int]]:
        """Run SELECT with JOIN, GROUP BY, and COUNT (sync)"""
        stmt: Select = (
            select(group_by_col, func.count(primary_cls.id))
            .join(join_cls, join_condition)
            .where(*filters)
            .group_by(group_by_col)
        )
        result = session.execute(stmt)
        return result.all()

    def count_where(
        self,
        session: Session,
        cls: Type[Base],
        *filters: BinaryExpression
    ) -> int:
        """Count rows in `cls` matching given filters (sync)"""
        stmt = select(func.count()).select_from(cls).where(*filters)
        result = session.execute(stmt)
        return result.scalar_one()