import requests
from datetime import datetime, timedelta
from token_manager import TokenManager

from datetime import datetime

#def get_event_filtered(start_date: str, end_date: str, subject_filter: str = ""):
def get_event_filtered(subject_filter=""):
    """
    Busca eventos entre datas específicas e filtra por assunto.
    Usa o endpoint /me/events e filtra via Python.
    
    start_date e end_date devem estar em ISO 8601 (ex: "2025-04-19T00:00:00").
    """
    start_date = datetime.now()
    #end_date será start_date + 1 dia
    end_date = start_date + timedelta(days=1)
    print("📅 Buscando eventos com filtros...")
    timezone="America/Sao_Paulo"
    tm = TokenManager()
    access_token = tm.get_access_token()

    url = "https://graph.microsoft.com/v1.0/me/events?$top=200"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": f'outlook.timezone="{timezone}"',
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Erro: {response.status_code} - {response.text}")
        return []

    eventos = response.json().get("value", [])
    resultado = []

    # Converte datas para comparação
    dt_inicio = datetime.fromisoformat(start_date)
    dt_fim = datetime.fromisoformat(end_date)

    for ev in eventos:
        assunto = ev.get("subject", "")
        inicio_str = ev["start"].get("dateTime")
        fim_str = ev["end"].get("dateTime")

        # Converte para datetime real
        inicio = datetime.fromisoformat(inicio_str)
        fim = datetime.fromisoformat(fim_str)

        # Aplica filtros
        if dt_inicio <= inicio <= dt_fim and subject_filter.lower() in assunto.lower():
            resultado.append({
                "id": ev["id"],
                "assunto": assunto or "(sem assunto)",
                "inicio": inicio_str,
                "fim": fim_str,
                "local": ev.get("location", {}).get("displayName", "(sem local)")
            })

    print(f"✅ {len(resultado)} evento(s) encontrados.")
    return resultado


def get_todo_tasks(list_name=None):
    """
    Busca tarefas da conta do usuário no Microsoft To Do.
    Se list_name não for passado, busca todas as listas.
    """
    print("📝 Buscando lembretes no To Do...")

    tm = TokenManager()
    access_token = tm.get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Obter listas
    lists_url = "https://graph.microsoft.com/v1.0/me/todo/lists"
    lists_response = requests.get(lists_url, headers=headers)
    if lists_response.status_code != 200:
        print("⚠️ Erro ao obter listas:", lists_response.text)
        return []

    todo_lists = lists_response.json().get("value", [])
    resultado = []

    for l in todo_lists:
        if list_name and list_name.lower() not in l["displayName"].lower():
            continue

        list_id = l["id"]
        tasks_url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks"
        tasks_response = requests.get(tasks_url, headers=headers)

        if tasks_response.status_code != 200:
            print(f"⚠️ Erro na lista {l['displayName']}: {tasks_response.text}")
            continue

        tasks = tasks_response.json().get("value", [])
        for task in tasks:
            resultado.append({
                "lista": l["displayName"],
                "titulo": task.get("title"),
                "status": task.get("status"),
                "vencimento": task.get("dueDateTime", {}).get("dateTime", "sem data")
            })

    return resultado


def create_event(assunto, inicio, fim, local="Online"):
    tm = TokenManager()
    access_token = tm.get_access_token()

    url = "https://graph.microsoft.com/v1.0/me/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    evento = {
        "subject": assunto,
        "start": {"dateTime": inicio, "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": fim, "timeZone": "America/Sao_Paulo"},
        "location": {"displayName": local}
    }

    resp = requests.post(url, headers=headers, json=evento)
    if resp.status_code in (200, 201):
        print("✅ Evento criado com sucesso.")
        return resp.json()
    else:
        print(f"❌ Erro ao criar evento: {resp.status_code} - {resp.text}")
        return None

def delete_event(event_id):
    tm = TokenManager()
    access_token = tm.get_access_token()

    url = f"https://graph.microsoft.com/v1.0/me/events/{event_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    resp = requests.delete(url, headers=headers)
    if resp.status_code == 204:
        print("✅ Evento apagado com sucesso.")
        return True
    else:
        print(f"❌ Erro ao apagar evento: {resp.status_code} - {resp.text}")
        return False


def create_reminder(titulo, status="notStarted"):
    tm = TokenManager()
    access_token = tm.get_access_token()

    url = "https://graph.microsoft.com/v1.0/me/todo/lists/Tasks/tasks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    tarefa = {
        "title": titulo,
        "status": status  # Ex: notStarted, inProgress, completed
    }

    resp = requests.post(url, headers=headers, json=tarefa)
    if resp.status_code in (200, 201):
        print("✅ Lembrete criado.")
        return resp.json()
    else:
        print(f"❌ Erro ao criar lembrete: {resp.status_code} - {resp.text}")
        return None


def delete_reminder(task_id):
    tm = TokenManager()
    access_token = tm.get_access_token()

    url = f"https://graph.microsoft.com/v1.0/me/todo/lists/Tasks/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    resp = requests.delete(url, headers=headers)
    if resp.status_code == 204:
        print("✅ Lembrete apagado.")
        return True
    else:
        print(f"❌ Erro ao apagar lembrete: {resp.status_code} - {resp.text}")
        return False

    
teste = get_event_filtered()
print(teste)