import uuid
import os
import re
from datetime import datetime
from dotenv import load_dotenv

from langchain.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import tiktoken

from typing import Optional

from pydantic import BaseModel, Field
from typing import List

#Importações de script
from mail import get_emails, delete_email_by_id
from contacts import get_contacts, delete_contacts_by_id
from outlook_calendar import create_event, delete_event, create_reminder, delete_reminder, get_event_filtered


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

# ====== CONTAGEM DE TOKENS ======
def print_token_usage(label, message, model_name="gpt-4"):
    num_tokens = count_tokens(message, model_name=model_name)
    print(f"🧮 {label} – Tokens: {num_tokens}")

def count_tokens(message, model_name="gpt-4"):
    """
    Conta tokens usando a biblioteca tiktoken.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(message))




# ====== FUNÇÕES E FERRAMENTAS ======

def generate_thread_id():
    return str(uuid.uuid4())

def get_current_datetime(args=None) -> datetime:
    current_date = datetime.now()
    print(f"📅 Data e hora atual: {current_date}")
    return current_date


# ====== FERRAMENTAS ======
#Definição do Schema para a ferramenta de deletar e-mails
class DeleteEmailsInput(BaseModel):
    message_ids: List[str]


#Definição do Schema para a ferramenta de deletar contatos
class DeleteContactsInput(BaseModel):
    contact_ids: List[str]

class GetContactsSchema(BaseModel):
    name_filter: str
    limit: Optional[int] = 100


class GetEventFilteredSchema(BaseModel):
    start_date: str = Field(..., description="Data de início no formato ISO 8601, ex: '2025-04-19T00:00:00'")
    end_date: str = Field(..., description="Data de fim no formato ISO 8601, ex: '2025-04-21T23:59:59'")
    subject_filter: Optional[str] = Field(None, description="Texto para filtrar eventos pelo assunto (case-insensitive)")

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-04-19T00:00:00",
                "end_date": "2025-04-21T23:59:59",
                "subject_filter": "reunião",
            }
        }

tools = [
    Tool(
        name="GetCurrentDateTime",
        func=get_current_datetime,
        description="Retorna a data e hora atual. Use para verificar o horário e poder informar ao usuário se ele tem e-mails recentes",
    ),
    Tool(
        name="GetEmails",
        func=get_emails,
        description=(
            "Busca e-mails da caixa de entrada. "
            "Pode filtrar por status ('unread', 'read' ou 'all'), por assunto, (exemplo: get_emails(\"unread\", limit=10, mark_as_read=False, subject_keyword=None))"
            "e decidir se os e-mails devem ser marcados como lidos. Marque o e-mail como lido, a não ser que o usuário diga o contrário. "
            "Exemplos: "
            "'Buscar e-mails não lidos sobre reunião', "
            "'Listar os e-mails lidos com assunto projeto', "
            "'Buscar todos os e-mails recentes e marcar como lidos'."
            "Quando responder, retorne o assunto e a data de recebimento dos e-mails em horário local. "
        )
    ),
    Tool(
    name="DeleteEmailById",
    func=delete_email_by_id,
    description=("Apaga e-mails pelo ID. Use com IDs retornados pela função GetEmails, caso solicitado."
                 "A ferramenta está preparada para receber uma lista de um ou mais IDs de e-mails. Mesmo que seja apenas um valor, mande como uma lista. "
                 ),
    args_schema=DeleteEmailsInput,
    return_direct=False, 
    ),
    Tool(
        name="GetContacts",
        func=get_contacts,
        description=(
            "Busca contatos do usuário. "
            "Pode filtrar por nome ou e-mail. "
            "Exemplos: "
            "'Listar contatos com o nome João', "
            "'Buscar contatos com o e-mail'"
        ),
        args_schema=GetContactsSchema,
    ),
    Tool(
        name="DeleteContactById",
        func=delete_contacts_by_id,
        description=("Apaga contatos pelo ID. Use com IDs retornados pela função GetContacts, caso solicitado."
                     "A ferramenta está preparada para receber uma lista de um ou mais IDs de contatos. Mesmo que seja apenas um valor, mande como uma lista. "
                     ),
        args_schema=DeleteContactsInput,
        return_direct=False, 
    ),
    #função de buscar eventos
    Tool(
        name="GetEvents",
        func=get_event_filtered,
        description=(
            "Busca eventos do calendário do usuário. não precisa de parametros. "
            '''
            "Pode filtrar por assunto, data de início e data de término. "
            "Exemplos: "
            "'Listar eventos da semana', "
            "'Buscar eventos com o assunto reunião', "
            "'Procurar eventos entre 01/01/2024 e 31/12/2024'"
            '''
        ),
        #args_schema=GetEventFilteredSchema,
    ),

]   

# ====== AGENTE REACT COM MEMÓRIA ======
memory = MemorySaver()

agent_executor = create_react_agent(
    model=chat,
    tools=tools,
    #reasoning="zero-shot-react-description",
    checkpointer=memory,
    prompt=("Você é um assistente Pessoal. Responda às perguntas do usuário com clareza e precisão. Não retorne o Thinking Processing para o usuário."
            ),
    #response_format="text",
)

# ====== CHATBOT STREAMING ======

def chatbot(user_input, thread_id):
    config = {"configurable": {"thread_id": thread_id, "recursion_limit": 50}}
    content = user_input["content"]

    # Compressão do prompt (usando middle-out)
    compressed_content = content  # compress_middle_out(content, max_length=200)

    # Extraindo o nome do modelo para contagem de tokens
    model_name = OPENROUTER_MODEL if MODE == "openrouter" else LOCAL_MODEL
    model_name = model_name.split("/")[1]  # Pegando a parte após a barra

    # Log de tokens do input
    print_token_usage("🔹 Input do usuário", compressed_content)

    total_output_tokens = 0  # Variável para acumular os tokens da saída

    for step, metadata in agent_executor.stream(
        {"messages": [HumanMessage(content=compressed_content)]},
        config,
        stream_mode="messages",
    ):
        print(f" {step}")
        if metadata["langgraph_node"] == "agent" and (text := step.text()):
            # Log de tokens da resposta
            num_tokens = count_tokens(text)
            total_output_tokens += num_tokens
            #print_token_usage("🔸 Resposta do agente (parcial)", text)
            yield text

    # Exibir o total de tokens da saída
    print(f"🔸 Total de tokens da saída: {total_output_tokens}")