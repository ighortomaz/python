from flask import Flask, request, jsonify
import threading
import queue
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta, timezone
import requests
from urllib.parse import urlparse
import psycopg2

load_dotenv()

class CustomFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__("%(asctime)s - %(name)s -- [%(levelname)s] >> %(message)s", "%Y-%m-%d %H:%M:%S", *args, **kwargs)

LOGGER = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

app = Flask(__name__)

# Criar uma fila para processar eventos de forma assíncrona
event_queue = queue.Queue()

# Configurar conexão com o MySQL

database_url = 'postgresql://ighortomaz:63UGnZSKTjkSy8uwggrcogdOcA89CB91@dpg-cvir99muk2gs73av0dag-a.virginia-postgres.render.com/monitoramento_db_k8n6'


# Parse a URL para extrair as partes do banco de dados
url = urlparse(database_url)

# Configurar a conexão
db_config = {
    "host": url.hostname,
    "port": url.port,
    "user": url.username,
    "password": url.password,
    "database": url.path[1:]  # O nome do banco está após a primeira barra "/"
}

url_operador = "https://exemplo.com/alerta-sessao"

def get_db_connection():
    return pymysql.connect(**db_config)

def processar_eventos():
    """ Processa eventos do webhook e insere no banco de dados """
    while True:
        dados = event_queue.get()
        if dados is None:
            break
        
        user_id = dados["user_id"]
        evento = dados["event"]
        timestamp = dados.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                if evento == "login":
                    cursor.execute(""" 
                        INSERT INTO sessoes (user_id, login_time) 
                        VALUES (%s, %s);
                    """, (user_id, timestamp))
                elif evento == "logout":
                    cursor.execute("""
                        UPDATE sessoes 
                        SET logout_time = %s 
                        WHERE user_id = %s AND logout_time IS NULL;
                    """, (timestamp, user_id))
            conn.commit()
            conn.close()
            LOGGER.info(f"Evento processado: {user_id} - {evento}")
        except Exception as e:
            LOGGER.error(f"Erro ao processar evento: {e}")

# Inicia a thread do processador
threading.Thread(target=processar_eventos, daemon=True).start()

@app.route("/webhook", methods=["POST"])
def receber_webhook():
    """ Recebe eventos de login/logout via webhook """
    dados = request.json  
    if not dados or "user_id" not in dados or "event" not in dados:
        return jsonify({"status": "erro", "mensagem": "Dados inválidos"}), 400
    
    event_queue.put(dados)
    
    return jsonify({"status": "sucesso", "mensagem": "Dados recebidos"}), 200

def monitorar_sessoes():
    """ Verifica sessões ativas e alerta sessões acima de 60 minutos """
    while True:
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, login_time 
                    FROM sessoes 
                    WHERE logout_time IS NULL AND alerta_enviado = FALSE;
                """)
                sessoes = cursor.fetchall()

                for sessao in sessoes:
                    login_time = sessao["login_time"]

                    # Garantir que o login_time esteja no formato correto de datetime com fuso horário UTC
                    login_time = login_time.replace(tzinfo=timezone.utc)

                    # Calcular o tempo de sessão
                    tempo_online = (datetime.now(timezone.utc) - login_time).total_seconds() #/ 60  # Convertido para minutos

                    if tempo_online > 1:  # Sessão maior que 60 minutos
                        user_id = sessao["user_id"]
                        LOGGER.warning(f"⚠️ Usuário {user_id} logado há {tempo_online:.2f} minutos!")

                        # Enviar alerta para a casa de apostas
                        try:
                            requests.post(url_operador, json={"user_id": user_id, "alerta": "sessao_long"})
                            LOGGER.info(f"🔔 Alerta enviado para {user_id}")
                        except Exception as e:
                            LOGGER.error(f"Erro ao enviar alerta: {e}")

                        # Atualizar o banco para marcar o alerta como enviado
                        cursor.execute("""
                            UPDATE sessoes 
                            SET alerta_enviado = TRUE 
                            WHERE id = %s;
                        """, (sessao["id"],))
                        conn.commit()

            conn.close()
        except Exception as e:
            LOGGER.error(f"Erro no monitoramento: {e}")

        # Espera 30 segundos antes de checar novamente
        threading.Event().wait(30)

# Iniciar monitoramento em uma thread separada
threading.Thread(target=monitorar_sessoes, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
