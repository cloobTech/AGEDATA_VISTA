from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from api.v1.utils.get_db_session import get_db_session
from services.users.user import (get_all_users, get_user_by_id, update_user,
                                 delete_user, upload_user_picture, get_user_notifications, get_user_report_statistics)

from api.v1.utils.current_user import get_current_user
from models.user import User


router = APIRouter(tags=['Users'], prefix='/api/v1/users')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_users(session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get all users"""
    try:
        response = await get_all_users(session)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(user_id: str, params: str = Query(None),  session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get a user by its ID"""
    try:
        response = await get_user_by_id(user_id, params, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{user_id}', status_code=status.HTTP_200_OK)
async def update_user_route(user_id: str, user_data: dict, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Update a user"""
    try:
        response = await update_user(user_id, user_data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except DataRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/{user_id}/profile_picture', status_code=status.HTTP_200_OK)
async def upload_user_picture_route(user_id: str, file: UploadFile, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Upload a user picture"""
    try:
        response = await upload_user_picture(file, user_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user_route(user_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Delete a user"""
    try:
        response = await delete_user(user_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{user_id}/notifications', status_code=status.HTTP_200_OK)
async def notifications(user_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """User's Notification"""
    try:
        response = await get_user_notifications(user_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{user_id}/statistics', status_code=status.HTTP_200_OK)
async def report_statistics(user_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """User's Notification"""
    try:
        response = await get_user_report_statistics(user_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
