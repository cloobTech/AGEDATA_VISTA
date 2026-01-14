from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRequest(BaseModel):
    session_id: str
    message: str
