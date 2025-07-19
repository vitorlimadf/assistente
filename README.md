# Assistente Pessoal com Ollama, OpenRouter, LangGraph, FastAPI e React

Este projeto implementa um assistente pessoal de linguagem natural que roda localmente, combinando:

- [LangGraph](https://github.com/langchain-ai/langgraph) para orquestração de agentes
- [LangChain](https://github.com/langchain-ai/langchain) para ferramentas, memória e integração
- [Ollama](https://ollama.com) para execução local de modelos de linguagem (LLMs)
- [FastAPI](https://fastapi.tiangolo.com/) servindo uma API e WebSocket
- [React](https://react.dev/) para a interface web moderna
- [OpenRouter](https://openrouter.ai/) adicionado posteriormente para casos de limitação de hardware

---

## Requisitos

- Python 3.10 ou superior  
- [Ollama](https://ollama.com/download) instalado  
- Git instalado  

---

## Instalação

### 1. Clone este repositório

```bash
git clone https://github.com/vitorlimadf/assistente.git
cd assistente
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## Baixando o Modelo

Antes de executar o assistente, baixe um modelo local com Ollama:

```bash
ollama pull mistral
```

Outros modelos compatíveis (falta testar todos):

- `llama3`
- `openchat`
- `gemma`
- `nous-hermes2`

Você pode alternar o modelo utilizado alterando o nome no código ou utilizando uma variável de ambiente (`LLM_MODEL`).

---

## Executando o Assistente

### 1. (Opcional) Inicie manualmente o servidor do Ollama

```bash
ollama serve
```

Na maioria dos casos, isso ocorre automaticamente em segundo plano.

### 2. Inicie a API com FastAPI

```bash
uvicorn server:app --reload
```

Abra o navegador em [http://localhost:8000](http://localhost:8000). O front-end React é servido diretamente pela aplicação.

---

## Estrutura do Projeto

```
📁 seu-repositorio/
├── server.py            # API FastAPI com WebSocket
├── frontend/            # Aplicação React
├── agente_graph.py      # Lógica do agente com LangGraph + Ollama + OpenRouter
├── token_manager        # gerenciamento de tokens de acesso para conectar ao e-mail
├── requirements.txt     # Dependências do projeto
└── README.md            # Este arquivo
```

---

## Banco de Dados Local

As conversas agora são armazenadas em um arquivo SQLite (`conversations.db`)
na raiz do projeto. O banco é criado automaticamente na primeira execução.
Caso queira utilizar outro caminho, altere a constante `DB_PATH` em
`conversation_storage.py`.

Os títulos das conversas são gerados automaticamente pela IA na primeira
resposta. Na barra lateral agora é possível pesquisar tanto pelos títulos
quanto pelo conteúdo das mensagens para localizar conversas antigas com
mais facilidade.

Para renomear ou excluir uma conversa, utilize o botão de três pontinhos (⋯)
alinhado à direita do título da conversa na barra lateral. Após clicar nesse
botão, um pequeno menu é exibido com as opções **Renomear** e **Excluir**. Ao
escolher "Renomear", aparece um campo de texto para definir o novo título; já
"Excluir" requer uma confirmação antes de remover o chat da lista.

---

## Observações Técnicas

A classe `ChatOllama` foi migrada para o pacote `langchain-ollama`. Para evitar avisos de depreciação:

```bash
pip install -U langchain-ollama
```

E utilize:

```python
from langchain_ollama import ChatOllama
```

A interface web possui um botão de microfone para ditar perguntas por voz. A
fala é transcrita automaticamente antes do envio ao assistente.

---


TODO: Atualizar com informações de como conectar ao e-mail

## Executando os Testes

Para garantir que tudo está funcionando corretamente, rode a suíte de testes:

```bash
pip install pytest
pytest
```

## Licença

Este projeto é open-source e pode ser utilizado, modificado e redistribuído livremente, conforme os termos da licença incluída no repositório.

Desenvolvido por Vitor Lima (E pelo ChatGPT, é claro :)
