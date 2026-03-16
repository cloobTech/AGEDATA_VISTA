from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends,  HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse, PlainTextResponse
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from api.v1.utils.get_db_session import get_db_session
from services.file_upload.upload_file_class import file_upload_service
from services.file_upload.upload_progress import task_progress_service
from services.sse.server_sent_events import sse_service
# from services.data_processing.helper.select_uploader_type import select_upload_processor
from services.data_processing.user_files.crud import update_user_file, delete_user_file, get_user_file_by_id
from storage.redis_client import get_task_progress, get_temp_data
from schemas.default_response import DefaultResponse
from schemas.upload_dataset import UploadForm
from api.v1.utils.current_user import get_current_user
from models.user import User
from storage import db
from models.uploaded_file import UploadedFile


router = APIRouter(tags=['File Upload'], prefix='/api/v1/file-upload')


def get_upload_form(
    user_id: str | None = Form(None),
    file_type: str = Form("tabular"),
    clean_file: bool = Form(False),
    source_type: str = Form('upload'),
    file_url: str | None = Form(None),
) -> UploadForm:
    return UploadForm(
        user_id=user_id if user_id else None,
        file_type=file_type,
        clean_file=clean_file,
        source_type=source_type,
        file_url=file_url
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def list_user_files(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DefaultResponse:
    """List all files for the currently authenticated user"""
    try:
        from sqlalchemy import select as sa_select
        from models.uploaded_file import UploadedFile as _UF
        result = await session.execute(sa_select(_UF).where(_UF.user_id == current_user.id))
        files = result.scalars().all()
        return DefaultResponse(
            status="success",
            message="Files retrieved successfully",
            data=[f.to_dict() for f in files],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@router.post("/", status_code=status.HTTP_200_OK)
async def upload_file(
    form: UploadForm = Depends(get_upload_form),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
) -> DefaultResponse:
    """
    Upload file for processing
    """
    form.user_id = current_user.id
    try:
        # Convert Pydantic model to dict for service
        form_dict = {
            "user_id": form.user_id,
            "file_type": form.file_type,
            "clean_file": form.clean_file,
            "source_type": form.source_type,
            "file_url": form.file_url
        }

        form_data, file_content = await file_upload_service.prepare_upload_data(
            file, form_dict
        )

        result = await file_upload_service.start_file_processing(form_data, file_content)

        return DefaultResponse(
            status="success",
            message="File submitted for processing",
            data=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@router.get("/upload-progress/{task_id}")
async def stream_task_progress(task_id: str, request: Request):
    """
    Stream task progress via Server-Sent Events
    """
    return await sse_service.stream_task_progress(task_id, request)


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get current task status (one-time check)
    """
    status_data = await task_progress_service.get_task_status(task_id)
    return DefaultResponse(
        status="success",
        message="Task status retrieved",
        data=status_data
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return DefaultResponse(
        status="success",
        message="File upload service is healthy",
        data={"service": "file-upload"}
    )


@router.get('/{file_id}/status', status_code=status.HTTP_200_OK)
async def get_file_upload_status(file_id: str,  current_user: User = Depends(get_current_user)) -> Optional[Dict[str, Any]]:
    """Get file upload status by id"""
    try:
        # response = await get_temp_data(file_id)  # Fetch temporary data instead
        # Fetch temporary data instead
        response = await get_task_progress(file_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{file_id}', status_code=status.HTTP_200_OK)
async def get_file_by_id(file_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DefaultResponse:
    """Get file by id"""
    try:
        response = await get_user_file_by_id(file_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{file_id}/download', status_code=status.HTTP_200_OK)
async def download_file(file_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Download file by redirecting to its storage URL"""
    try:
        file = await db.get(session, UploadedFile, file_id)
        if not file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        if not file.url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File URL not available")
        return RedirectResponse(url=file.url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{file_id}', status_code=status.HTTP_200_OK)
async def update_file(file_id: str, data: dict,  session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DefaultResponse:
    """Update file by id"""
    try:
        response = await update_user_file(file_id, data, session)
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


@router.get('/{file_id}/content', status_code=status.HTTP_200_OK)
async def get_file_content(
    file_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Return the raw CSV content of an uploaded file as text/plain.
    Tries local disk first, then external URL, to avoid CORS issues."""
    import os
    import logging
    log = logging.getLogger(__name__)

    try:
        file = await db.get(session, UploadedFile, file_id)
        if not file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_id}")

        # Compute backend root from this file's location:
        # uploaded_file.py → routes → v1 → api → backend
        _here = os.path.dirname(os.path.abspath(__file__))
        backend_root = os.path.normpath(os.path.join(_here, '..', '..', '..'))
        uploads_datasets = os.path.join(backend_root, 'uploads', 'datasets')

        def _read_text(path: str) -> str | None:
            """Read a file as text, return None if it doesn't exist or is empty."""
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
                return content if content.strip() else None
            except Exception:
                return None

        # ── Strategy 1: resolve file.url as a local path ──────────────────────
        if file.url and not file.url.startswith('http'):
            # e.g. "/uploads/datasets/{id}_{name}.{ext}"
            candidate = os.path.normpath(os.path.join(backend_root, file.url.lstrip('/')))
            content = _read_text(candidate)
            if content:
                log.info("get_file_content: serving from url-derived path %s", candidate)
                return PlainTextResponse(content=content, media_type="text/plain")

        # ── Strategy 2: construct path from record fields {id}_{name}.{ext} ──
        if file.name and file.extension:
            candidate = os.path.join(uploads_datasets, f"{file.id}_{file.name}.{file.extension}")
            content = _read_text(candidate)
            if content:
                log.info("get_file_content: serving from reconstructed path %s", candidate)
                return PlainTextResponse(content=content, media_type="text/plain")

        # ── Strategy 3: scan uploads/datasets/ for any file prefixed by id ────
        if os.path.isdir(uploads_datasets):
            for fname in os.listdir(uploads_datasets):
                if fname.startswith(f"{file.id}_"):
                    fpath = os.path.join(uploads_datasets, fname)
                    content = _read_text(fpath)
                    if content:
                        log.info("get_file_content: serving from prefix-scan %s", fpath)
                        return PlainTextResponse(content=content, media_type="text/plain")

        # ── Strategy 4: fetch external URL (Cloudinary / Supabase / http) ─────
        if file.url and file.url.startswith('http'):
            log.info("get_file_content: fetching external url %s", file.url)
            try:
                async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                    resp = await client.get(file.url)
                    if resp.status_code == 200:
                        text = resp.text
                        stripped = text.strip()
                        if not (stripped.startswith('<!') or stripped.lower().startswith('<html')):
                            return PlainTextResponse(content=text, media_type="text/plain")
                        log.warning("get_file_content: external url returned HTML, not CSV")
                    else:
                        log.warning("get_file_content: external url returned %s", resp.status_code)
            except Exception as exc:
                log.warning("get_file_content: external url fetch failed: %s", exc)

        # ── Nothing worked ─────────────────────────────────────────────────────
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"File content could not be retrieved. "
                f"id={file.id}, url={file.url}, "
                f"name={file.name}, extension={file.extension}. "
                f"The file may have been moved or deleted from storage."
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{file_id}', status_code=status.HTTP_200_OK)
async def delete_file(file_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DefaultResponse:
    """Delete file by id"""
    try:
        response = await delete_user_file(file_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
