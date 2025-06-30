from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from api.v1.utils.get_db_session import get_db_session
from schemas.default_response import DefaultResponse
from services.notifications.crud import get_notification_by_id, delete_notification, update_notification


router = APIRouter(tags=['Notification'], prefix='/api/v1/notifications')


@router.get('/{notification_id}', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def get_notification_by_id_route(notification_id: str, session: AsyncSession = Depends(get_db_session)):
    """Get notification by id"""
    try:
        notification = await get_notification_by_id(notification_id, session)
        return notification
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{notification_id}', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def delete_notification_route(notification_id: str, session: AsyncSession = Depends(get_db_session)):
    """Delete notification"""
    try:
        notification = await delete_notification(notification_id, session)
        return notification
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{notification_id}', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def update_notification_route(notification_id: str, notification_data: dict, session: AsyncSession = Depends(get_db_session)):
    """Update notification"""
    try:
        notification = await update_notification(notification_id, notification_data, session)
        return notification
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
