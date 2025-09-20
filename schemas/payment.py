from pydantic import BaseModel

class SubscriptionInit(BaseModel):
    plan_id: str