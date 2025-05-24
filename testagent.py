from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_redis import RedisChatMessageHistory
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
import pymongo

# Load environment variables
load_dotenv()

class UserInfo(BaseModel):
    name: str = Field(..., description="Full name of the user")
    phone: str = Field(..., description="Phone number of the user")
    email: str = Field(..., description="Email address of the user")    


# Setup
search = GoogleSerperAPIWrapper()
REDIS_URL = "redis://localhost:6379"
limit = 20

def get_redis_history(session_id: str):
    return RedisChatMessageHistory(session_id=session_id, redis_url=REDIS_URL)

# Tools
@tool
def get_exchange_rate_from_api(currency_from: str, currency_to: str) -> str:
    """
    Return the exchange rate between currencies
    Args:
        currency_from: str
        currency_to: str
    """
    url = f"https://api.frankfurter.app/latest?from={currency_from}&to={currency_to}"
    api_response = requests.get(url)
    return api_response.text


MONGODB_URI = os.getenv("MONGODB_URI", mongo_uri="mongodb+srv://nisha:nisha@ragcluster.6zcesdr.mongodb.net/?retryWrites=true&w=majority&appName=RagCluster")
DB_NAME = "user_database"
COLLECTION_NAME = "users"



@tool
def store_user_info(user_info: UserInfo) -> str:
    """
    Stores user information including name, phone number, and email in MongoDB.
    Use this when the user provides their personal information.
    """
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Insert document
        result = collection.insert_one(user_info.dict())
        return f"User information stored successfully with ID: {result.inserted_id}"
    except Exception as e:
        return f"Error storing user information: {str(e)}"

@tool
def magic_function(input: int) -> int:
    """Applies a magic function to an input."""
    return input + 2

@tool
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

@tool
def google_search(query: str):
    """
    Perform a search on Google
    Args:
        query: the information to be retrieved with google search
    """
    return search.run(query)

# Tool list
langchain_tool = [
    get_exchange_rate_from_api,
    magic_function,
    add_numbers,
    multiply_numbers,
    google_search
]

# Language Model
llm = ChatGoogleGenerativeAI(
    temperature=0.5,
    model="gemini-2.0-flash"
)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create agent
agent = create_tool_calling_agent(llm, langchain_tool, prompt)
agent_executor = AgentExecutor(agent=agent, tools=langchain_tool, verbose=True)

# Memory integration
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_redis_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# FastAPI app
app = FastAPI()

class ChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = "foo"

class ChatResponse(BaseModel):
    output: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    config = {"configurable": {"session_id": request.session_id}}
    try:
        result = agent_with_chat_history.invoke({"input": request.input}, config)
        output_str = result.get("output", "No output generated.")
        return ChatResponse(output=output_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
