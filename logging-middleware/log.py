import os
import requests

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

LOG_API_URL = "http://4.224.186.213/evaluation-service/logs"

def Log(stack, level, package, message):

    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            LOG_API_URL,
            json=payload,
            headers=headers
        )
        return response.json()

    except Exception as e:
        print(f"Logging Failed: {e}")
