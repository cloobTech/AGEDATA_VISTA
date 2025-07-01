from typing import AsyncGenerator, Type, Any
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from models import user, project, project_member, project_invitation, notification, uploaded_file, report, notification_recipient
from models.base_model import Base
from sqlalchemy.sql import Select


class DBStorage:
    """Database storage class"""

    MODELS = {
        'User': user.User,
        'Project': project.Project,
        'ProjectMember': project_member.ProjectMember,
        'ProjectInvitation': project_invitation.ProjectInvitation,
        'Notification': notification.Notification,
        'UploadedFile': uploaded_file.UploadedFile,
        'Report': report.Report,
        'NotificationRecipient': notification_recipient.NotificationRecipient
    }

    __engine = None
    __session_maker = None

    def __init__(self, db_uri: str):
        """Initialize the database storage class"""
        self.__engine = create_async_engine(db_uri, echo=False)
        self.__session_maker = async_sessionmaker(
            self.__engine, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create and return a session object"""
        async with self.__session_maker() as session:
            yield session

    async def reload(self):
        """Reload the database schema"""
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        """Drop all tables in the database"""
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def new(self, session: AsyncSession, obj: Type[Base]):
        """Add objects to the current database session"""
        session.add(obj)

    def add_all(self, session: AsyncSession, data: list[Type[Base]]):
        """Add Batch"""
        session.add_all(data)

    async def save(self, session: AsyncSession):
        """Commit all changes of the current database session."""
        await session.commit()

    async def rollback(self, session: AsyncSession):
        """Roll back the current database session."""
        await session.rollback()

    async def delete(self, session: AsyncSession, obj: Type[Base]):
        """Delete an object from the current database session"""
        await session.delete(obj)
        await self.save(session)

    async def find_by(self, session: AsyncSession, cls: Type[Base], **kwargs: Any) -> Type[Base] | None:
        """Retrieves one object based on a class name and kwargs (class attribute)"""
        query_result = await session.execute(select(cls).filter_by(**kwargs))
        return query_result.scalars().first()

    async def filter(self, session: AsyncSession, cls: Type[Base], *args: BinaryExpression, fetch_one: bool = False) -> Base | list[Base] | None:
        """Retrieve objects based on filters"""

        query_result = await session.execute(select(cls).filter(*args))
        result = query_result.scalars()

        return result.first() if fetch_one else result.all()

    async def all(self, session: AsyncSession, cls: Type[Base] | None = None) -> dict:
        """Query all objects of a specific class or all models."""
        objects = {}
        if cls is not None:
            result = await session.execute(select(cls))
            result = result.scalars().all()
            for obj in result:
                obj_reference = f'{type(obj).__name__}.{obj.id}'
                objects[obj_reference] = obj
        else:
            for model in self.MODELS.values():
                result = await session.execute(select(model))
                result = result.scalars().all()
                for obj in result:
                    obj_reference = f'{type(obj).__name__}.{obj.id}'
                    objects[obj_reference] = obj
        return objects

    async def get(self, session: AsyncSession, cls: Type[Base], obj_id: str) -> Base | None:
        """Retrieve a single object by its class and ID."""
        if cls and obj_id:
            result = await session.execute(select(cls).filter(cls.id == obj_id))
            return result.scalar_one_or_none()  # Returns exactly one object or None
        return None

    async def filter_join(
        self,
        session: AsyncSession,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        *filters: BinaryExpression,
    ) -> list[Base]:
        """
        Run a SELECT with JOIN and filters.
        Example:
        await db.filter_join(
            session,
            Notification,
            NotificationRecipient,
            Notification.id == NotificationRecipient.notification_id,
            NotificationRecipient.user_id == user_id
        )
        """
        stmt: Select = (
            select(primary_cls)
            .join(join_cls, join_condition)
            .where(*filters)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count(self, session: AsyncSession, cls: Type[Base] | None = None) -> int:
        """Return the count of all objects in storage"""
        objects = await self.all(session, cls)
        return len(objects)

    async def filter_join_pair(
        self,
        session: AsyncSession,
        primary_cls: Type[Base],
        join_cls: Type[Base],
        join_condition: BinaryExpression,
        *filters: BinaryExpression,
    ) -> list[tuple[Base, Base]]:
        """
        Run a SELECT with JOIN and return (A, B) tuples.
        """
        stmt = (
            select(primary_cls, join_cls)
            .join(join_cls, join_condition)
            .where(*filters)
        )
        result = await session.execute(stmt)
        return result.all()
