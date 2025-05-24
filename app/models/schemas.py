from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = "foo"

class ChatResponse(BaseModel):
    output: str
