from typing import AsyncGenerator, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.sql.expression import BinaryExpression

from models.base_model import Base


class DBStorage:
    """ Database storage class """

    MODELS = {

    }

    __engine = None
    __session_maker = None

    def __init__(self, db_uri: str = 'sqlite+aiosqlite:///db.sqlite3'):
        """ Initialize the database storage class """

        self.__engine = create_async_engine(db_uri, echo=False)
        self.__session_maker = async_sessionmaker(
            self.__engine, expire_on_commit=False)

    async def _session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create and return a session object"""
        async with self.__session_maker() as session:
            if session is None:
                raise RuntimeError("DatabaseSessionManager is not initialized")
            async with session.begin():
                yield session

    async def db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create and return a session object"""
        async with self.__session_maker() as session:
            if session is None:
                raise RuntimeError("DatabaseSessionManager is not initialized")
            async with session.begin():
                yield session

    async def reload(self):
        """Reload the database schema"""
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        """Drop all tables in the database"""
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def new(self, obj: Type[Base]):
        """Add objects to the current database session"""
        async for session in self._session():
            session.add(obj)

    async def add_all(self, data: list[Type[Base]]):
        """Add Batch"""
        async for session in self._session():
            session.add_all(data)

    async def save(self, session: AsyncSession = None):
        """Commit all changes of the current database session."""
        if not session:
            async for session in self._session():
                await session.commit()
        else:
            await session.commit()

    async def rollback(self, session: AsyncSession = None):
        """Roll back the current database session."""
        if not session:
            async for session in self._session():
                await session.rollback()
        else:
            await session.rollback()

    async def delete(self, obj: Type[Base | None] = None):
        """Delete an object from the current database session if not None"""
        if obj:
            async for session in self._session():
                await session.delete(obj)
                await self.save()

    async def find_by(self, cls: Type[Base], **kwargs: Any) -> Type[Base] | None:
        """retrieves one object based on a class name and kwargs (class attribute)"""
        async for session in self._session():
            query_result = await session.execute(select(cls).filter_by(**kwargs))
            result = query_result.scalars().first()
            if result:
                return result
        return None

    async def filter(self, cls: Type[Base], *args: BinaryExpression, fetch_one: bool = False,) -> dict:
        """retrieves all objects based on a class name and kwargs (class attribute)"""
        objects = {}
        async for session in self._session():
            query_result = await session.execute(select(cls).filter(*args))
            if fetch_one:  # Fetch a single object
                result = query_result.scalars().first()
                return result
            result = query_result.scalars().all()
            for obj in result:
                obj_reference = f'{type(obj).__name__}.{obj.id}'
                objects[obj_reference] = obj
        return objects

    async def shutdown_db(self):
        """Close current DB session"""
        async for session in self._session():
            await session.close()

    async def merge(self, obj: Type[Base]):
        """Merge the current session with the object"""
        async for session in self._session():
            merged_obj = await session.merge(obj)
            return merged_obj

    async def all(self, cls: Type[Base] | None = None) -> dict:
        """Query all objects of a specific class or all models."""
        objects = {}
        try:
            async for session in self._session():
                # If a class is provided, query only that class
                if cls is not None:
                    result = await session.execute(select(cls))
                    result = result.scalars().all()
                    for obj in result:
                        obj_reference = f'{type(obj).__name__}.{obj.id}'
                        objects[obj_reference] = obj
                    return objects

                # If no class is provided, query all models in MODELS
                for model in self.MODELS.values():
                    result = await session.execute(select(model))
                    result = result.scalars().all()
                    for obj in result:
                        obj_reference = f'{type(obj).__name__}.{obj.id}'
                        objects[obj_reference] = obj

        except Exception as e:
            # Log the exception for debugging
            print(f"Error in `all` method: {e}")

        return objects

    async def get(self, cls: Type[Base], obj_id: str) -> Base | None:
        """Retrieve a single object by its class and ID."""
        if cls and obj_id:
            try:
                async for session in self._session():
                    result = await session.execute(select(cls).filter(cls.id == obj_id))
                    return result.scalar_one_or_none()  # Returns exactly one object or None
            except Exception as e:
                # Log the exception for debugging
                print(f"Error in `get` method: {e}")

        return None

    def count(self, cls: Type[Base] | None = None) -> int:
        """Return the count of all objects in storage"""
        return (len(self.all(cls)))
