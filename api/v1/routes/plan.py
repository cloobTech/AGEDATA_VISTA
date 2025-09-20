from fastapi import APIRouter, Depends,  HTTPException, status
from errors.exceptions import EntityNotFoundError, DataRequiredError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from services.payments.plan import create_plan, get_all_plans, get_plan_by_id, update_plan, delete_plan
from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user
from models.user import User


router = APIRouter(tags=['Plans'], prefix='/api/v1/plans')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_plans(session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get all plans"""
    try:
        response = await get_all_plans(session)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{plan_id}', status_code=status.HTTP_200_OK)
async def get_plan(plan_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get a plan by its ID"""
    try:
        response = await get_plan_by_id(plan_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_plan_route(plan_data: dict, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Create a new plan"""
    try:
        response = await create_plan(plan_data, session)
        return response
    except DataRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Plan with this name already exists.") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{plan_id}', status_code=status.HTTP_200_OK)
async def update_plan_route(plan_id: str, plan_data: dict, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Update a plan"""
    try:
        response = await update_plan(plan_id, plan_data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{plan_id}', status_code=status.HTTP_200_OK)
async def delete_plan_route(plan_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Delete a plan"""
    try:
        response = await delete_plan(plan_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
