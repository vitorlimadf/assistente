import streamlit as st
from agente_graph import generate_thread_id, chatbot, generate_conversation_title
from conversation_storage import (
    save_conversation,
    load_conversation,
    list_conversations,
    delete_conversation,
    rename_conversation,
)
import asyncio


st.title("Assistente Virtual - Chatbot")


# desloca o container do User um pouco pra direita, similar ao ChatGPT
st.markdown(
    "<style>.st-emotion-cache-janbn0 {margin-left: 100px;}</style>",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# verifica se existe um uid de sessão
if "uid" not in st.session_state:
    st.session_state.uid = generate_thread_id()
if "title" not in st.session_state:
    st.session_state.title = None

with st.sidebar:
    st.header("Conversas")
    search = st.text_input("Buscar")
    convs = [
        (tid, title)
        for tid, title in list_conversations()
        if not search or search.lower() in (title or "").lower()
    ]
    for tid, title in convs:
        cols = st.columns([0.9, 0.1])
        label = title if title else tid[:8]
        if cols[0].button(label, key=f"conv-{tid}", use_container_width=True):
            st.session_state.messages = load_conversation(tid)
            st.session_state.uid = tid
            st.session_state.title = title
            st.rerun()
        with cols[1].popover("\u22ee", key=f"menu-{tid}"):
            new_title = st.text_input("Novo título", value=title or "", key=f"rename-{tid}")
            if st.button("Renomear", key=f"btn-rename-{tid}") and new_title:
                rename_conversation(tid, new_title)
                if st.session_state.uid == tid:
                    st.session_state.title = new_title
                st.rerun()
            if st.button("Excluir", key=f"btn-del-{tid}"):
                delete_conversation(tid)
                if st.session_state.uid == tid:
                    st.session_state.messages = []
                    st.session_state.uid = generate_thread_id()
                    st.session_state.title = None
                st.rerun()

    st.divider()
    if st.button("Nova conversa"):
        st.session_state.messages = []
        st.session_state.uid = generate_thread_id()
        st.session_state.title = None
        st.rerun()


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
    if st.session_state.title is None and len(st.session_state.messages) >= 2:
        st.session_state.title = generate_conversation_title(st.session_state.messages)
    save_conversation(
        st.session_state.uid,
        st.session_state.messages,
        title=st.session_state.title,
    )
