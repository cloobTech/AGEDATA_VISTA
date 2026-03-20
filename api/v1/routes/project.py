from fastapi import APIRouter, Depends,  HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError, EntityConflictError, APermissionError
from services.projects.project import create_project, get_all_projects, get_project_by_id, update_project, delete_project
from services.projects.project_invitation import invite_project_member, respond_to_invitation
from services.projects.project_member import remove_project_member, update_project_member_access
from api.v1.utils.get_db_session import get_db_session
from schemas.project import CreateProject
from schemas.default_response import DefaultResponse
from api.v1.utils.current_user import get_current_user
from models.user import User
from models.project_member import ProjectMember


router = APIRouter(tags=['Projects'], prefix='/api/v1/projects')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_projects(session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Get projects owned by or shared with the current user"""
    try:
        response = await get_all_projects(session, user_id=current_user.id)
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


@router.get('/{project_id}/members', status_code=status.HTTP_200_OK)
async def get_project_members(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """List all members of a project"""
    try:
        from sqlalchemy import select as sa_select
        result = await session.execute(
            sa_select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        members = result.scalars().all()
        return DefaultResponse(
            status="success",
            message="Members retrieved",
            data=[m.to_dict() for m in members]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{project_id}/members/{member_id}', status_code=status.HTTP_200_OK)
async def remove_member_route(
    project_id: str,
    member_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from a project"""
    try:
        data = {
            "project_id": project_id,
            "member_id": member_id,
            "acting_user_id": current_user.id,
        }
        response = await remove_project_member(data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except APermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{project_id}/members/{member_id}', status_code=status.HTTP_200_OK)
async def update_member_role_route(
    project_id: str,
    member_id: str,
    body: dict,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Update a project member's role"""
    try:
        data = {
            "project_id": project_id,
            "member_id": member_id,
            "acting_user_id": current_user.id,
            **body,
        }
        response = await update_project_member_access(data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except APermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
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
