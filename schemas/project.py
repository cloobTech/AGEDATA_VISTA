from pydantic import BaseModel


class CreateProject(BaseModel):
    """Create Project"""
    title: str
    description: str
    owner_id: str
    visibility: str = "public"
