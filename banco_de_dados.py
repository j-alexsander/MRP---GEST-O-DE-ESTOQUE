import sqlite3

db = sqlite3.connect('controle_de_estoque.db')

def criar_tabelas():
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS controle_de_estoque(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            categoria TEXT,
            valor REAL,
            quantidade INTEGER,
            estoque_minimo INTEGER
    )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS movimentacoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        tipo TEXT,
        motivo TEXT,
        quantidade INTEGER
    )
    """)

    db.commit()
    db.close()