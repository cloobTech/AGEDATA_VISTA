from fastapi import APIRouter
from schemas.chat import AgentRequest
from services.ai_chats.chat import chat

router = APIRouter(tags=['Agent Chat'], prefix='/api/v1/ai-agent')


@router.post("", status_code=200)
def chat_endpoint(req: AgentRequest):
    reply = chat(
        session_id=req.session_id,
        user_message=req.message,
    )
    return {"reply": reply}
