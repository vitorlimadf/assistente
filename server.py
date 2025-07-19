from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from agente_graph import chatbot, generate_thread_id, generate_conversation_title
from conversation_storage import (
    save_conversation,
    load_conversation,
    list_conversations,
    search_conversations,
    delete_conversation,
    rename_conversation,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    thread_id = generate_thread_id()
    messages = []
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "chat":
                content = data.get("content", "")
                messages.append({"role": "user", "content": content})
                text_response = ""
                for chunk in chatbot({"content": content}, thread_id=thread_id):
                    text_response += chunk
                    await websocket.send_json({"type": "chunk", "content": chunk})
                messages.append({"role": "assistant", "content": text_response})
                title = generate_conversation_title(messages) if len(messages) == 2 else None
                save_conversation(thread_id, messages, title=title)
                await websocket.send_json({"type": "end"})
            elif action == "load":
                thread_id = data.get("thread_id", thread_id)
                messages = load_conversation(thread_id)
                await websocket.send_json({"type": "history", "messages": messages})
            elif action == "reset":
                thread_id = generate_thread_id()
                messages = []
                await websocket.send_json({"type": "history", "messages": messages})
    except WebSocketDisconnect:
        pass


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/api/conversations")
def api_list_conversations(search: str = ""):
    """Return stored conversations optionally filtered by search."""
    convs = search_conversations(search) if search else list_conversations()
    return [{"thread_id": tid, "title": title} for tid, title in convs]


@app.post("/api/conversations/{thread_id}/rename")
def api_rename_conversation(thread_id: str, data: dict):
    new_title = data.get("title")
    if not new_title:
        raise HTTPException(status_code=400, detail="missing title")
    rename_conversation(thread_id, new_title)
    return {"status": "ok"}


@app.delete("/api/conversations/{thread_id}")
def api_delete_conversation(thread_id: str):
    delete_conversation(thread_id)
    return {"status": "ok"}
