from fastapi import APIRouter, Depends,  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from services.projects.project import create_project, get_all_projects, get_project_by_id, update_project, delete_project
from api.v1.utils.get_db_session import get_db_session
from schemas.project import CreateProject


router = APIRouter(tags=['Projects'], prefix='/api/v1/projects')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_projects(session: AsyncSession = Depends(get_db_session)):
    """Get all projects"""
    try:
        response = await get_all_projects(session)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{project_id}', status_code=status.HTTP_200_OK)
async def get_project(project_id: str, session: AsyncSession = Depends(get_db_session)):
    """Get a project by its ID"""
    try:
        response = await get_project_by_id(project_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{project_id}', status_code=status.HTTP_200_OK)
async def update_project_route(project_id: str, project_data: dict, session: AsyncSession = Depends(get_db_session)):
    """Update a project"""
    try:
        response = await update_project(project_id, project_data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e) from e
    except DataRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{project_id}', status_code=status.HTTP_200_OK)
async def delete_project_route(project_id: str, session: AsyncSession = Depends(get_db_session)):
    """Delete a project"""
    try:
        response = await delete_project(project_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_new_project(project_data: CreateProject, session: AsyncSession = Depends(get_db_session)):
    """Create a new project"""
    try:
        response = await create_project(project_data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
