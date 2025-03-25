from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import csv
import os

app = FastAPI()

# 📌 Conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect("jogoseguro.db")
    conn.row_factory = sqlite3.Row  # Permite acessar as colunas pelos nomes
    return conn

# 📌 Função para Registrar Alertas no Banco de Dados
def registrar_alerta(user_id: str, tipo: str, mensagem: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO alertas (user_id, tipo, mensagem) VALUES (?, ?, ?)",
        (user_id, tipo, mensagem),
    )
    
    conn.commit()
    conn.close()

# 📌 Modelos de Dados
class Usuario(BaseModel):
    user_id: str
    nome: str
    email: str
    data_nascimento: str

class Deposito(BaseModel):
    user_id: str
    valor: float

class Monitoramento(BaseModel):
    user_id: str
    tempo_jogado_minutos: int

class Aposta(BaseModel):
    user_id: str
    valor: float

# 📌 Endpoint 1: Registrar Usuário
@app.post("/user/register", summary="Registrar um novo usuário")
def register_user(usuario: Usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (user_id, nome, email, data_nascimento) VALUES (?, ?, ?, ?)",
            (usuario.user_id, usuario.nome, usuario.email, usuario.data_nascimento),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return {"message": "Usuário já cadastrado!"}
    finally:
        conn.close()
    
    return {"message": "Usuário registrado com sucesso!", "user_id": usuario.user_id}

# 📌 Endpoint 2: Registrar Tempo de Jogo
@app.post("/monitoring/activity", summary="Registrar tempo de jogo")
def register_activity(data: Monitoramento):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO monitoramento (user_id, tempo_jogado) VALUES (?, ?)",
        (data.user_id, data.tempo_jogado_minutos),
    )
    conn.commit()

    cursor.execute(
        "SELECT SUM(tempo_jogado) FROM monitoramento WHERE user_id = ?",
        (data.user_id,),
    )
    total_tempo = cursor.fetchone()[0] or 0

    conn.close()

    if total_tempo >= 180:
        registrar_alerta(data.user_id, "Tempo de Jogo", f"Usuário jogou {total_tempo} minutos sem pausa.") 
        return {
            "alert": f"Você está jogando há muito tempo sem pausa ({total_tempo} min). Recomendamos um intervalo.",
            "confirmar": "Clique em 'Ciente' para continuar."
        }

    return {"message": "Tempo de jogo registrado.", "tempo_total_jogado": total_tempo}

# 📌 Endpoint 3: Gerar Relatório em CSV
@app.get("/report/csv/{user_id}", response_class=FileResponse, summary="Gerar relatório CSV para um usuário", tags=["Relatórios"])
def generate_csv_report(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔍 Buscar dados do usuário
    cursor.execute("SELECT nome, email FROM usuarios WHERE user_id = ?", (user_id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        return {"message": "Usuário não encontrado."}

    nome, email = usuario["nome"], usuario["email"]

    # 🔍 Buscar estatísticas do usuário
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

    # 🔍 Criar o arquivo CSV
    csv_filename = f"relatorio_{user_id}.csv"
    csv_path = os.path.join(os.getcwd(), csv_filename)

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

        writer.writerow([])
        writer.writerow(["Alertas Recebidos"])
        writer.writerow(["Data", "Tipo", "Mensagem"])
        for alerta in alertas:
            writer.writerow([alerta["data"], alerta["tipo"], alerta["mensagem"]])

    # 📎 Retornar o arquivo CSV para download
    return FileResponse(csv_path, filename=csv_filename, media_type="text/csv")

# ✅ Exibir os endpoints registrados corretamente após a definição de app
if __name__ == "__main__":
    print("✅ Endpoints registrados:")
    for route in app.routes:
        print(f"🔹 {route.path}")