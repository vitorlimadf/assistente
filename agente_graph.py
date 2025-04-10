import os
import sys
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain.tools import Tool
from dotenv import load_dotenv
import uuid
from datetime import datetime


import os
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
#from langgraph.graph import StateGraph

load_dotenv() 

# Carrega chave da API do OpenRouter
OPENROUTER_API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL", "openchat/openchat-3.5")

# Define o modelo e a base do endpoint do OpenRouter
chat = ChatOpenAI(
    openai_api_key=OPENROUTER_API_KEY,
    model_name=MODEL_NAME,  # ou outro modelo disponível no OpenRouter
    base_url="https://openrouter.ai/api/v1"  # Endpoint da API do OpenRouter
)




def generate_thread_id():
    return str(uuid.uuid4())


def get_current_datetime(args=None) -> datetime:
    current_date = datetime.now()
    print(f"Data e hora atual: {current_date}")
    return current_date



tools = [
    Tool(
        name="GetCurrentDateTime",
        func=get_current_datetime,
        description="Retorna a data e hora atual.",
    ),
]



# Configuração da memória do agente
memory = MemorySaver()

# Criação do agente com create_react_agent
agent_executor = create_react_agent(
    model=chat,
    tools=tools,
    checkpointer=memory,
    prompt=(
        "Você é um assistente útil. Responda às perguntas do usuário com clareza e precisão. "
    ),
    #    response_format="text"
)


# Função principal do chatbot
def chatbot(user_input, thread_id):

    config = {"configurable": {"thread_id": thread_id, "session_timeout": 3600}}
    #config = {"configurable": {"thread_id": "abc123", "session_timeout": 3600}}

    # user_input = input("Digite sua mensagem: ")  # Solicita a entrada do usuário
    for step, metadata in agent_executor.stream(
        {
            "messages": [HumanMessage(content=user_input["content"])]
        },  # Usa a entrada do teclado
        config,
        stream_mode="messages",
    ):
        if metadata["langgraph_node"] == "agent" and (text := step.text()):
            yield text


# if __name__ == "__main__":
#    chatbot()