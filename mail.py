import requests
import re
from token_manager import TokenManager # ajuste conforme seu projeto
from pprint import pprint

def get_emails(status="unread", limit=10, mark_as_read=True, subject_keyword=None):
    """
    status: 'unread', 'read' ou 'all'
    limit: quantidade máxima de e-mails a retornar
    mark_as_read: se True, marca os e-mails como lidos após recuperar
    subject_keyword: string opcional para filtrar e-mails por assunto
    """
    print("🔄 Iniciando a obtenção de e-mails...")

    # Inicializando o TokenManager
    tm = TokenManager()
    access_token = tm.get_access_token()
    print(f"✅ Token de acesso obtido: {access_token[:10]}...")  # Mostra os primeiros 10 caracteres do token
  
    # Definindo o filtro de status
    status_filter = {
        "unread": "isRead eq false",
        "read": "isRead eq true",
        "all": None
    }

    filters = []
    if status_filter.get(status):
        filters.append(status_filter[status])
        print(f"🔍 Filtro de status aplicado: {status_filter[status]}")
    else:
        print(f"⚠️ Status inválido fornecido: {status}. Considerando 'all'.")

    if subject_keyword:
        filters.append(f"contains(subject,'{subject_keyword}')")
        print(f"🔍 Filtro de assunto aplicado: {subject_keyword}")

    # Montando a URL de requisição
    url = "https://graph.microsoft.com/v1.0/me/messages"
    #usando o client_id
    #url = f"https://graph.microsoft.com/v1.0/users/{tm.user_name}/messages"

    query_parts = []
    if filters:
        query_parts.append(f"$filter={' and '.join(filters)}")
        print(f"🔍 Filtros aplicados: {filters}")

    query_parts.append("$orderby=receivedDateTime desc")
    query_parts.append(f"$top={limit}")
    url += "?" + "&".join(query_parts)

    print(f"🔗 URL final da requisição: {url}")

    # Configurando os cabeçalhos da requisição
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "ConsistencyLevel": "eventual"
    }

    # Realizando a requisição
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Erro ao buscar e-mails: {response.status_code} - {response.text}")
        return f"Erro ao buscar e-mails: {response.status_code} - {response.text}"

    print(f"✅ Requisição bem-sucedida! Status code: {response.status_code}")

    messages = response.json().get("value", [])
    if not messages:
        print("⚠️ Nenhum e-mail encontrado com esse filtro.")
        return "Nenhum e-mail encontrado com esse filtro."

    emails = []
    print(f"📥 Encontrados {len(messages)} e-mails.")

    for msg in messages:
        msg_id = msg["id"]
        subject = msg["subject"]
        sender = msg["from"]["emailAddress"]["address"]
        received = msg["receivedDateTime"]

        # Limpando o corpo do e-mail
        body = format_body(msg["body"]["content"])

        # Adicionando o e-mail à lista
        emails.append({
            "id": msg_id,
            "subject": subject,
            "from": sender,
            "receivedDateTime": received,
            "body": body,
        })

        if mark_as_read and not msg.get("isRead", True):
            patch_url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}"
            patch_data = {"isRead": True}
            patch_response = requests.patch(patch_url, headers=headers, json=patch_data)
            if patch_response.status_code != 200:
                print(f"⚠️ Erro ao marcar como lido: {patch_response.status_code} - {patch_response.text}")
            else:
                print(f"✅ E-mail {msg_id} marcado como lido.")

    print(f"📤 Processamento de e-mails concluído.")
    return emails

def delete_email_by_id(message_ids: list[str]):
    tm = TokenManager()
    access_token = tm.get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    results = {}

    for message_id in message_ids:
        url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        try:
            print(f"🗑️ Tentando deletar e-mail: {message_id}...")
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                print(f"✅ E-mail {message_id} deletado com sucesso.")
                results[message_id] = True
            else:
                print(f"❌ Erro ao deletar e-mail {message_id}: {response.status_code}")
                print(f"📄 Resposta da API: {response.text}")
                results[message_id] = False

        except requests.exceptions.RequestException as e:
            print(f"🚨 Exceção ao tentar deletar o e-mail {message_id}: {e}")
            results[message_id] = False

    return results




def format_body(html):
    # Converte <a href="URL">texto</a> para [texto](URL)
    def replace_link(match):
        href = match.group(1).strip()
        texto = match.group(2).strip()
        return f"[{texto}]({href})"

    # Converte links
    html = re.sub(r'<a\s+[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', replace_link, html, flags=re.DOTALL | re.IGNORECASE)

    # Remove <style> e outras tags
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'&nbsp;|&#160;', ' ', html)

    # Compactação: remove espaços duplicados e linhas em branco
    html = re.sub(r'\s+', ' ', html)               # múltiplos espaços → um espaço
    html = re.sub(r'(\n\s*){2,}', '\n', html)       # múltiplas quebras de linha → uma
    html = html.strip()

    return html
