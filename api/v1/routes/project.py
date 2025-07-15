from fastapi import APIRouter, Depends,  HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError, EntityConflictError, APermissionError
from services.projects.project import create_project, get_all_projects, get_project_by_id, update_project, delete_project
from services.projects.project_invitation import invite_project_member, respond_to_invitation
from api.v1.utils.get_db_session import get_db_session
from schemas.project import CreateProject
from api.v1.utils.current_user import get_current_user
from models.user import User


router = APIRouter(tags=['Projects'], prefix='/api/v1/projects')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_projects(session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get all projects"""
    try:
        response = await get_all_projects(session)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{project_id}', status_code=status.HTTP_200_OK)
async def get_project(project_id: str, params: str = Query(None),  session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get a project by its ID"""
    try:
        response = await get_project_by_id(project_id, params, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{project_id}', status_code=status.HTTP_200_OK)
async def update_project_route(project_id: str, project_data: dict, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Update a project"""
    try:
        response = await update_project(project_id, project_data, session)
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


@router.delete('/{project_id}', status_code=status.HTTP_200_OK)
async def delete_project_route(project_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Delete a project"""
    try:
        response = await delete_project(project_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_new_project(project_data: CreateProject, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Create a new project"""
    try:
        response = await create_project(project_data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/{project_id}/invitation', status_code=status.HTTP_200_OK)
async def invite_member(project_id: str, data: dict, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Invite a user to a project"""
    try:
        response = await invite_project_member(project_id, data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except APermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except EntityConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/{project_id}/invitation-response', status_code=status.HTTP_200_OK)
async def respond_to_project_invitation(project_id: str, data: dict, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Respond to a project invitation"""
    try:
        response = await respond_to_invitation(project_id, data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
