"""
Модуль для работы с GigaChat API.
"""

import requests
import json
import uuid

def zap(text, 
        client_id="068e6d69-232e-407c-9034-a983e7b43edf",
        client_secret="2c051802-dff1-4e96-9deb-57d5ce48483d",
        scope="GIGACHAT_API_PERS",
        api_url="https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        oauth_url="https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    ):
    """
    Отправляет запрос к GigaChat и возвращает ответ.
    Args:
        text (str): Текст запроса
        client_id (str): Client ID
        client_secret (str): Client Secret
        scope (str): OAuth scope
        api_url (str): URL GigaChat
        oauth_url (str): URL OAuth
    Returns:
        str: Ответ от GigaChat
    """
    # 1. Получение токена
    basic_token = f"{client_id}:{client_secret}".encode("utf-8")
    import base64
    basic_token_b64 = base64.b64encode(basic_token).decode("utf-8")
    headers_auth = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {basic_token_b64}'
    }
    data_auth = f'scope={scope}'
    resp = requests.post(oauth_url, headers=headers_auth, data=data_auth, verify=True)
    resp.raise_for_status()
    access_token = resp.json().get('access_token')
    if not access_token:
        raise Exception(f"Ошибка авторизации: {resp.text}")
    # 2. Генерация ответа
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        "model": "GigaChat-2-Max",
        "messages": [
            {"role": "system", "content": "Ты - помощник, который даёт чёткие и точные ответы. Не показывай процесс размышления, сразу давай правильный ответ. Если это математическая задача, покажи формулу и вычисления. Если это вопрос по программированию, давай готовый код. Если это общий вопрос, давай краткий и информативный ответ."},
            {"role": "user", "content": text}
        ],
        "profanity_check": True
    }
    resp2 = requests.post(api_url, headers=headers, data=json.dumps(payload), verify=True)
    resp2.raise_for_status()
    result = resp2.json()
    return result['choices'][0]['message']['content'] if 'choices' in result and result['choices'] else result 