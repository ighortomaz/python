import sqlite3
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 📌 Conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect("jogoseguro.db")
    conn.row_factory = sqlite3.Row
    return conn

# 📌 Função para gerar o PDF manualmente
def generate_pdf_report(user_id: str):
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

    cursor.execute("SELECT tipo, mensagem, data FROM alertas WHERE user_id = ? ORDER BY data DESC", (user_id,))
    alertas = cursor.fetchall()

    conn.close()

    # 🗂 Salvar na pasta "reports"
    pdf_filename = f"relatorio_{user_id}.pdf"
    pdf_path = os.path.join("reports", pdf_filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, f"Relatório do Usuário {user_id}")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Nome: {nome}")
    c.drawString(50, height - 120, f"E-mail: {email}")
    c.drawString(50, height - 140, f"Tempo Total de Jogo: {tempo_jogado} minutos")
    c.drawString(50, height - 160, f"Total de Apostas: {total_apostas}")
    c.drawString(50, height - 180, f"Média de Valor Apostado: R$ {media_apostas:.2f}")
    c.drawString(50, height - 200, f"Total de Depósitos: {total_depositos}")
    c.drawString(50, height - 220, f"Média de Valor Depositado: R$ {media_depositos:.2f}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 260, "Alertas Recebidos:")
    c.setFont("Helvetica", 12)
    y_position = height - 280
    for alerta in alertas:
        c.drawString(50, y_position, f"{alerta['data']} - {alerta['tipo']}: {alerta['mensagem']}")
        y_position -= 20

    c.save()
    return pdf_path
