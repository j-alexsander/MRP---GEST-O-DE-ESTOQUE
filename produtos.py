import banco_de_dados
import sqlite3

db = sqlite3.connect("controle_de_estoque.db")

cursor = db.cursor()

def cadastrar_produto():

    cursor = db.cursor()

    nome = input("Nome do produto: ")
    categoria = input("Categoria: ")
    valor = float(input("Valor: "))
    quantidade = int(input("Quantidade: "))
    estoque_minimo = int(input("Estoque mínimo: "))

    cursor.execute(""" INSERT INTO controle_de_estoque(
        produto, categoria, valor, quantidade, estoque_minimo)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, categoria, valor, quantidade, estoque_minimo))

    db.commit()
def ver_estoque():

    cursor = db.cursor()

    cursor.execute("SELECT * FROM controle_de_estoque")

    dados = cursor.fetchall()

    print("\nESTOQUE")
    print("-" * 50)

    for item in dados:
        print(item)

