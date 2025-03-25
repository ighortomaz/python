import sqlite3
import csv
import os

# 📌 Conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect("jogoseguro.db")
    conn.row_factory = sqlite3.Row
    return conn

# 📌 Função para gerar o CSV manualmente
def generate_csv_report(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, email FROM usuarios WHERE user_id = ?", (user_id,))
    usuario = cursor.fetchone()

    if not usuario:
        return None

    nome, email = usuario["nome"], usuario["email"]

    cursor.execute("SELECT SUM(tempo_jogado) FROM monitoramento WHERE user_id = ?", (user_id,))
    tempo_jogado = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*), AVG(valor) FROM apostas WHERE user_id = ?", (user_id,))
    total_apostas, media_apostas = cursor.fetchone()
    total_apostas = total_apostas or 0
    media_apostas = media_apostas or 0

    cursor.execute("SELECT COUNT(*), AVG(valor) FROM depositos WHERE user_id = ?", (user_id,))
    total_depositos, media_depositos = cursor.fetchone()
    total_depositos = total_depositos or 0
    media_depositos = media_depositos or 0

    conn.close()

    # 🗂 Salvar na pasta "reports"
    csv_filename = f"relatorio_{user_id}.csv"
    csv_path = os.path.join("reports", csv_filename)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Campo", "Valor"])
        writer.writerow(["Nome", nome])
        writer.writerow(["E-mail", email])
        writer.writerow(["Tempo Total de Jogo (min)", tempo_jogado])
        writer.writerow(["Total de Apostas", total_apostas])
        writer.writerow(["Média de Apostas", f"R$ {media_apostas:.2f}"])
        writer.writerow(["Total de Depósitos", total_depositos])
        writer.writerow(["Média de Depósitos", f"R$ {media_depositos:.2f}"])

    return csv_path
