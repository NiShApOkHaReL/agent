from fastapi import APIRouter, HTTPException
from app.services.agent_manager import AgentManager
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()
agent_manager = AgentManager()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    config = {"configurable": {"session_id": request.session_id}}
    try:
        result = agent_manager.invoke_agent({"input": request.input}, config)
        return ChatResponse(output=result.get("output", "No output generated."))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
