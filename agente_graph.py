import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

from langchain.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import requests
from token_manager import TokenManager

# ====== CARREGAR VARIÁVEIS DE AMBIENTE (.env) ======
load_dotenv()
OPENROUTER_API_KEY = os.getenv("API_KEY")
OPENROUTER_MODEL = os.getenv("MODEL", "openchat/openchat-3.5")

# ====== SELETOR DE PROVEDOR ======
# "local" → usa Ollama localmente
# "openrouter" → usa serviço online
MODE = os.getenv("MODE", "local")  # Altere aqui para "openrouter" se quiser mudar o provedor

# ====== MODELOS LOCAIS DISPONÍVEIS ======
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "mistral")  # Ex: mistral, openchat, llama3

# ====== INSTÂNCIA DO MODELO ======
if MODE == "openrouter":
    print(f"🌐 Usando modelo remoto via OpenRouter: {OPENROUTER_MODEL}")
    chat = ChatOpenAI(
        model_name=OPENROUTER_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,
        #max_tokens=200,
    )
else:
    print(f"🖥️ Usando modelo local via Ollama: {LOCAL_MODEL}")
    chat = ChatOllama(
        model=LOCAL_MODEL,
        base_url="http://localhost:11434",
        temperature=0.1,
        max_tokens=200,
    )

# ====== FUNÇÕES E FERRAMENTAS ======

def generate_thread_id():
    return str(uuid.uuid4())

def get_current_datetime(args=None) -> datetime:
    current_date = datetime.now()
    print(f"📅 Data e hora atual: {current_date}")
    return current_date

def search_emails_by_subject(subject_keyword: str):
    tm = TokenManager()
    access_token = tm.get_access_token()
    print("cadeia de pesquisa:", subject_keyword)
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages"
        f"?$search=\"subject:{subject_keyword}\"&$top=10"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "ConsistencyLevel": "eventual"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json().get("value", [])
        if not messages:
            return "Nenhum e-mail encontrado com esse assunto."
            
        #criando uma lista para ser preenchida com os e-mails encontrados
        emails = []
        for msg in messages:
            print(f"Assunto: {msg['subject']}")
            print(f"De: {msg['from']['emailAddress']['address']}")
            print(f"Recebido em: {msg['receivedDateTime']}")
            print("="*80)
            #criando uma lista de atributos para ser retornado com os dados do e-mail
            attributes = {
                "subject": msg["subject"],
                "from": msg["from"]["emailAddress"]["address"],
                "receivedDateTime": msg["receivedDateTime"],
                "body": msg["body"]["content"],
            }
            # Adicionando o dicionário de atributos à lista de e-mails
            emails.append(attributes)
        # Retornando a lista de e-mails encontrados
        return emails
    else:
        return "Erro ao buscar mensagens:", response.text

if __name__ == "__main__":
    termo = input("Buscar por assunto: ")
    search_emails_by_subject(termo)


tools = [
    Tool(
        name="GetCurrentDateTime",
        func=get_current_datetime,
        description="Retorna a data e hora atual. Use para verificar o horário e poder informar ao usuário se ele tem e-mails recentes",
    ),
        Tool(
        name="GetEmailsBySubject",
        func=search_emails_by_subject,
        description="Pesquisa E-mails por assunto. Exemplo: 'reunião'.",
    )
]

# ====== AGENTE REACT COM MEMÓRIA ======
memory = MemorySaver()

agent_executor = create_react_agent(
    model=chat,
    tools=tools,
    checkpointer=memory,
    prompt="Você é um assistente útil. Responda às perguntas do usuário com clareza e precisão. Não retorne o Thinking Processing para o usuário.",
    #response_format="text",
)

# ====== CHATBOT STREAMING ======

def chatbot(user_input, thread_id):
    config = {"configurable": {"thread_id": thread_id, "session_timeout": 3600}}

    for step, metadata in agent_executor.stream(
        {"messages": [HumanMessage(content=user_input["content"])]},
        config,
        stream_mode="messages",
    ):
        if metadata["langgraph_node"] == "agent" and (text := step.text()):
            yield text
