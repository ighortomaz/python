import sqlite3

# 📌 Conectar ao banco de dados SQLite (ou criar se não existir)
conn = sqlite3.connect("jogoseguro.db")
cursor = conn.cursor()

# 📌 Criar tabelas para armazenar os dados
cursor.executescript("""
CREATE TABLE IF NOT EXISTS usuarios (
    user_id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    data_nascimento TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS atividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tempo_jogado INTEGER NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
);

CREATE TABLE IF NOT EXISTS depositos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    valor REAL NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
);

CREATE TABLE IF NOT EXISTS questionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    respostas TEXT NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tipo TEXT NOT NULL,
    detalhes TEXT NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
);
""")

# 📌 Salvar as alterações e fechar a conexão inicial
conn.commit()
conn.close()
