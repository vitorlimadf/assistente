import streamlit as st
from agente_graph import generate_thread_id,chatbot
import asyncio


st.title("Teste sua RAG")

# desloca o container do User um pouco pra direita, similar ao ChatGPT
st.html("<style>.st-emotion-cache-janbn0 {margin-left: 100px;}</style>")

if "messages" not in st.session_state:
    st.session_state.messages = []

#verifica se existe um uid de sessão
if "uid" not in st.session_state:
    st.session_state.uid = generate_thread_id()


def print_sources(sources):
    if sources:
        with st.expander("_**FONTES** e respectivas relevâncias (range % não limitado):_", expanded=False):
            st.json(sources, expanded=True)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        sources = message.get("sources")
        print_sources(sources)

if prompt := st.chat_input("De que você precisa?"):
    #user_details = get_authenticated_user_details()
    #user_name = user_details.get("user_name")
    #print(f"tipo da variavel: {type(user_name)}")
    #print(user_name)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        #if userobj not in locals() :
        #    userobj = get_authenticated_user_details

        

        #print("messages")
        #print(messages)
        message_stream = chatbot(messages[-1], thread_id=st.session_state.uid)
        

        #print("message_stream")
        #print(message_stream)
    
        sources = []
        text_response = ''
        response_container = st.empty()

        for chunk in message_stream:
            if isinstance(chunk, list):
                sources = chunk
            else:
                text_response += chunk
                response_container.write(text_response)

    #    print_sources(sources)

    st.session_state.messages.append({"role": "assistant", "content": text_response, "sources": sources})


async def get_response():
    sources = []
    text_response = ''
    response_container = st.empty()

    async for chunk in message_stream:
        if isinstance(chunk, list):
            sources = chunk
        else:
            text_response += chunk
            response_container.write(text_response)

    print_sources(sources)