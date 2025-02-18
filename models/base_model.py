#!/usr/bin/python3
""" Base Model for other models to be used in this project """
from datetime import datetime, timezone
import json
import uuid
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from utils.parse_datetime import parse_and_format_datetime

# List of date fields
date_fields = ['token_created_at',
               'appointment_start_time', 'appointment_end_time', 'date_of_birth']

# format for datetime used within the app
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Base from sqlalchemy
class Base(DeclarativeBase):
    """Base Class from Sqlalchemy for table creation and deletion"""
    pass


class BaseModel:
    """ Base class for other classes in this project """
    id: Mapped[str] = mapped_column(
        String(60), nullable=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(timezone.utc))

    def __init__(self, *args, **kwargs):
        """
            instantiation of new BaseModel Class
        """
        if kwargs:
            self.__set_attrs(kwargs)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

    def __set_attrs(self, attr_dict: dict) -> None:
        """ set attributes """
        if "id" not in attr_dict:
            attr_dict['id'] = str(uuid.uuid4())
        if "created_at" not in attr_dict:
            attr_dict['created_at'] = datetime.now(timezone.utc)
        if "updated_at" not in attr_dict:
            attr_dict['updated_at'] = datetime.now(timezone.utc)

        # Convert date fields from strings to datetime objects
        for field in date_fields:
            if field in attr_dict and isinstance(attr_dict[field], str):
                attr_dict[field] = parse_and_format_datetime(attr_dict[field])

        if "_class_" in attr_dict:
            del attr_dict["_class_"]

        for key, value in attr_dict.items():
            setattr(self, key, value)

    def __is_serializable(self, obj: any) -> bool:
        """
            private: checks if object is serializable
        """
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):  # Catch specific exceptions
            return False

    def to_dict(self, exclude=None) -> dict:
        """
            returns a dictionary containing all keys/values of _dict_ of the instance
        """
        obj_class = self.__class__.__name__
        dict_obj = {}
        for key, value in self.__dict__.items():
            if self.__is_serializable(value):
                dict_obj[key] = value
            else:
                dict_obj[key] = str(value)  # convert to string
            if isinstance(value, datetime):
                dict_obj[key] = value.strftime(TIME_FORMAT)
        dict_obj["_class_"] = obj_class
        dict_obj.pop('_sa_instance_state', None)
        if obj_class == 'User':
            dict_obj.pop('password', None)
        if exclude:
            for key in exclude:
                dict_obj.pop(key, None)
        return dict_obj

    async def save(self, session: AsyncSession):
        """Add an object in the DB """
        self.updated_at = datetime.now(timezone.utc)
        session.add(self)
        await session.commit()

    async def delete(self, session: AsyncSession):
        """Delete an instance from the DB"""
        await session.delete(self)
        await session.commit()

    async def update(self, session: AsyncSession, dict_obj: dict = None):
        """Update a model"""
        ignore_list = [
            'id', 'created_at', 'updated_at'
        ]
        # List of date fields
        if dict_obj:
            updated_dict = {
                key: value for key, value in dict_obj.items() if key not in ignore_list
            }
            if '_class_' in updated_dict:
                del updated_dict['_class_']
             # Convert date fields from strings to datetime objects
            for field in date_fields:
                if field in updated_dict and isinstance(updated_dict[field], str):
                    updated_dict[field] = parse_and_format_datetime(
                        updated_dict[field])
            for key, value in updated_dict.items():
                setattr(self, key, value)
            await self.save(session)

    def _str_(self) -> str:
        """ string representation of our Model """
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"
