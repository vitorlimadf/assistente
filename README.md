# Assistente Pessoal com Ollama, OpenRouter, LangGraph e Streamlit

Este projeto implementa um assistente pessoal de linguagem natural que roda localmente, combinando:

- [LangGraph](https://github.com/langchain-ai/langgraph) para orquestração de agentes
- [LangChain](https://github.com/langchain-ai/langchain) para ferramentas, memória e integração
- [Ollama](https://ollama.com) para execução local de modelos de linguagem (LLMs)
- [Streamlit](https://streamlit.io/) para interface web simples e leve
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

### 2. Execute a interface web

```bash
streamlit run app.py
```

Acesse via navegador em [http://localhost:8501](http://localhost:8501)

---

## Estrutura do Projeto

```
📁 seu-repositorio/
├── app_graph.py         # Interface web com Streamlit
├── agente_graph.py      # Lógica do agente com LangGraph + Ollama + OpenRouter
├── token_manager        # gerenciamento de tokens de acesso para conectar ao e-mail
├── requirements.txt     # Dependências do projeto
└── README.md            # Este arquivo
```

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
