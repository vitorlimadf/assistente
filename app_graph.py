import streamlit as st
from agente_graph import (
    generate_thread_id,
    chatbot,
    generate_conversation_title,
)
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
    st.markdown(
        """
        <style>
        .conv-row div[data-testid="column"] {padding: 0 !important;}
        .conv-row button {border-radius: 0;}
        .conv-row button:first-child {border-top-left-radius: 0.5rem;border-bottom-left-radius: 0.5rem;}
        .conv-row button:last-child {border-top-right-radius: 0.5rem;border-bottom-right-radius: 0.5rem;width: 2.5rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "open_menu" not in st.session_state:
        st.session_state.open_menu = None
    if "menu_action" not in st.session_state:
        st.session_state.menu_action = None

    for tid, title in convs:
        st.markdown("<div class='conv-row'>", unsafe_allow_html=True)
        row = st.columns([0.88, 0.12], gap="0")
        label = title if title else tid[:8]
        if row[0].button(label, key=f"conv-{tid}", use_container_width=True):
            st.session_state.messages = load_conversation(tid)
            st.session_state.uid = tid
            st.session_state.title = title
            st.session_state.open_menu = None
            st.session_state.menu_action = None
            st.rerun()

        if row[1].button("\u22ee", key=f"btn-menu-{tid}"):
            if st.session_state.open_menu == tid:
                st.session_state.open_menu = None
                st.session_state.menu_action = None
            else:
                st.session_state.open_menu = tid
                st.session_state.menu_action = None

        if st.session_state.open_menu == tid:
            action = st.session_state.menu_action
            if action is None:
                col_ren, col_del = st.columns(2)
                if col_ren.button("Renomear", key=f"opt-rename-{tid}"):
                    st.session_state.menu_action = "rename"
                if col_del.button("Excluir", key=f"opt-del-{tid}"):
                    st.session_state.menu_action = "delete"
            elif action == "rename":
                new_title = st.text_input(
                    "Novo título", value=title or "", key=f"rename-{tid}"
                )
                col_save, col_cancel = st.columns(2)
                if col_save.button("Salvar", key=f"btn-save-{tid}") and new_title:
                    rename_conversation(tid, new_title)
                    if st.session_state.uid == tid:
                        st.session_state.title = new_title
                    st.session_state.open_menu = None
                    st.session_state.menu_action = None
                    st.rerun()
                if col_cancel.button("Cancelar", key=f"btn-cancel-{tid}"):
                    st.session_state.menu_action = None
            elif action == "delete":
                st.warning("Confirmar exclusão?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Confirmar", key=f"btn-conf-{tid}"):
                    delete_conversation(tid)
                    if st.session_state.uid == tid:
                        st.session_state.messages = []
                        st.session_state.uid = generate_thread_id()
                        st.session_state.title = None
                    st.session_state.open_menu = None
                    st.session_state.menu_action = None
                    st.rerun()
                if col_no.button("Cancelar", key=f"btn-no-{tid}"):
                    st.session_state.menu_action = None
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    if st.button("Nova conversa"):
        st.session_state.messages = []
        st.session_state.uid = generate_thread_id()
        st.session_state.title = None
        st.rerun()


def print_sources(sources):
    if sources:
        with st.expander(
            "_**FONTES** e respectivas relevâncias (range % não limitado):_",
            expanded=False,
        ):
            st.json(sources, expanded=True)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        sources = message.get("sources")
        print_sources(sources)

if prompt := st.chat_input("De que você precisa?"):
    # user_details = get_authenticated_user_details()
    # user_name = user_details.get("user_name")
    # print(f"tipo da variavel: {type(user_name)}")
    # print(user_name)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        # if userobj not in locals() :
        #    userobj = get_authenticated_user_details

        # print("messages")
        # print(messages)
        message_stream = chatbot(messages[-1], thread_id=st.session_state.uid)

        # print("message_stream")
        # print(message_stream)

        sources = []
        text_response = ""
        response_container = st.empty()

        for chunk in message_stream:
            if isinstance(chunk, list):
                sources = chunk
            else:
                text_response += chunk
                response_container.write(text_response)

    #    print_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": text_response, "sources": sources}
    )
    if st.session_state.title is None and len(st.session_state.messages) >= 2:
        st.session_state.title = generate_conversation_title(
            st.session_state.messages
        )
    save_conversation(
        st.session_state.uid,
        st.session_state.messages,
        title=st.session_state.title,
    )
