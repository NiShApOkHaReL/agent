from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_redis import RedisChatMessageHistory
from app.config.settings import settings
from app.services.tool_service import CurrencyTools, MathTools, SearchTools

class AgentManager:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            temperature=settings.gemini_temperature,
            model=settings.gemini_model
        )
        
        self.tools = [
            CurrencyTools.get_exchange_rate,
            MathTools.magic_function,
            MathTools.add,
            MathTools.multiply,
            SearchTools.google_search
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        self.agent_executor = AgentExecutor(
            agent=create_tool_calling_agent(self.llm, self.tools, self.prompt),
            tools=self.tools,
            verbose=True
        )
        
        self.agent_with_history = RunnableWithMessageHistory(
            self.agent_executor,
            self._get_redis_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def _get_redis_history(self, session_id: str):
        return RedisChatMessageHistory(
            session_id=session_id,
            redis_url=settings.redis_url
        )

    def invoke_agent(self, input_data: dict, config: dict):
        return self.agent_with_history.invoke(input_data, config)
