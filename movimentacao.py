import banco_de_dados
import sqlite3

db = sqlite3.connect('controle_de_estoque.db')

def entrada_produto():
    
    cursor = db.cursor()

    produto_id = int(input("ID do produto: "))
    quantidade = int(input("Quantidade entrada: "))
    motivo = input("Motivo: ")

    cursor.execute(""" UPDATE controle_de_estoque
        SET quantidade = quantidade + ?
        WHERE id = ?
        """, (quantidade, produto_id))

    cursor.execute(""" INSERT INTO movimentacoes
        (produto_id, tipo, motivo, quantidade)
        VALUES (?, ?, ?, ?)
        """, (produto_id, "entrada", motivo, quantidade))

    db.commit()
    print("Entrada realizada!")


def saida_produto():

    cursor = db.cursor()

    produto_id = int(input("ID do produto: "))
    quantidade = int(input("Quantidade saída: "))
    motivo = input("Motivo: ")

    cursor.execute(""" SELECT quantidade
        FROM controle_de_estoque
        WHERE id = ?
        """, (produto_id,))

    resultado = cursor.fetchone()

    if resultado is None:
        print("Produto não encontrado")
        return

    estoque_atual = resultado[0]

    if quantidade > estoque_atual:
        print("Estoque insuficiente")
        return

    cursor.execute("""UPDATE controle_de_estoque
        SET quantidade = quantidade - ?
        WHERE id = ?
    """, (quantidade, produto_id))

    cursor.execute("""INSERT INTO movimentacoes
    (produto_id, tipo, motivo, quantidade)
    VALUES (?, ?, ?, ?)
    """, (produto_id, "saida", motivo, quantidade))

    db.commit()

    print("Saída realizada!")