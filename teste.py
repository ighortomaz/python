import psycopg2
import os

# URL do banco
DATABASE_URL = "postgresql://ighortomaz:63UGnZSKTjkSy8uwggrcogdOcA89CB91@dpg-cvir99muk2gs73av0dag-a/monitoramento_db_k8n6"

def get_db_connection():
    """ Conecta ao banco de dados PostgreSQL """
    try:
        # Conexão ao banco
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')  # sslmode='require' para conexão segura
        print("✅ Conectado ao PostgreSQL!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

# Testar a conexão
conn = get_db_connection()
if conn:
    conn.close()

