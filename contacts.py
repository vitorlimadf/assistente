import requests
from token_manager import TokenManager

def get_contacts(name_filter=None, limit=100):
    """
    Busca contatos do usuário.
    name_filter: filtra contatos pelo início do displayName
    limit: número máximo de contatos a retornar
    """
    print("📇 Buscando contatos...")

    tm = TokenManager()
    access_token = tm.get_access_token()
    print(f"🔐 Token obtido: {access_token[:10]}...")

    url = "https://graph.microsoft.com/v1.0/me/contacts"
    query_parts = []

    if name_filter:
        query_parts.append(f"$filter=startswith(displayName,'{name_filter}')")
        print(f"🔍 Aplicado filtro de nome: {name_filter}")

    query_parts.append(f"$top={limit}")
    url += "?" + "&".join(query_parts)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Erro ao buscar contatos: {response.status_code} - {response.text}")
        return []

    contatos = response.json().get("value", [])
    if not contatos:
        print("⚠️ Nenhum contato encontrado com esse filtro.")
        return "Nenhum e-mail encontrado com esse filtro."
    
    print(f"📥 {len(contatos)} contato(s) encontrados.")
    resultado = []

    for contato in contatos:
        contato_id = contato["id"]
        nome = contato.get("displayName", "(sem nome)")
        #email = contato.get("emailAddresses", [{}])[0].get("address", "(sem e-mail)")
        telefone = contato.get("mobilePhone", "(sem telefone)")

        print(f"➡️ {nome} - {telefone}")
        resultado.append({
            "id": contato_id,
            "nome": nome,
            "telefone": telefone
        })

    return resultado


def delete_contact(contact_id):
    """
    Remove um contato específico pelo ID.
    """
    print(f"🚨 Solicitando exclusão do contato {contact_id}...")

    tm = TokenManager()
    access_token = tm.get_access_token()

    url = f"https://graph.microsoft.com/v1.0/me/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("🗑️ Contato removido com sucesso.")
        return True
    else:
        print(f"⚠️ Erro ao apagar contato: {response.status_code} - {response.text}")
        return False



def delete_contacts_by_id(contact_ids: list[str]):
    """
    Apaga vários contatos com base em uma lista de IDs.
    Retorna um dicionário com o status de cada tentativa.
    """
    print("🧹 Iniciando exclusão de contatos...")

    tm = TokenManager()
    access_token = tm.get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    results = {}

    for contact_id in contact_ids:
        url = f"https://graph.microsoft.com/v1.0/me/contacts/{contact_id}"
        try:
            print(f"🗑️ Tentando deletar contato: {contact_id}...")
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                print(f"✅ Contato {contact_id} deletado com sucesso.")
                results[contact_id] = True
            else:
                print(f"❌ Erro ao deletar contato {contact_id}: {response.status_code}")
                print(f"📄 Resposta da API: {response.text}")
                results[contact_id] = False

        except requests.exceptions.RequestException as e:
            print(f"🚨 Exceção ao tentar deletar o contato {contact_id}: {e}")
            results[contact_id] = False

    print("✅ Processo de exclusão finalizado.")
    return results