import banco_de_dados
import sqlite3
from datetime import datetime

db = sqlite3.connect("controle_de_estoque.db")

def ver_movimentacoes():

    cursor = db.cursor()

    cursor.execute("SELECT * FROM movimentacoes")
    dados = cursor.fetchall()

    print("\nMOVIMENTAÇÕES")
    print("-" * 50)

    for mov in dados:
        print(mov)

def giro_estoque():
    
    print("\nGIRO DE ESTOQUE")

    cmv = float(input("Digite o CMV: "))
    estoque_inicial = float(input("Digite o estoque inicial: "))
    estoque_final = float(input("Digite o estoque final: "))

    estoque_medio = (estoque_inicial + estoque_final) / 2

    if estoque_medio == 0:
        print("Não é possível dividir por zero")
        return

    giro = cmv / estoque_medio

    print(f"Giro de Estoque: {giro:.2f}")

def nivel_servico():

    print("\nNÍVEL DE SERVIÇO")

    pedidos_prazo = int(input("Pedidos entregues no prazo: "))
    total_pedidos = int(input("Total de pedidos: "))

    if total_pedidos == 0:
        print("Total de pedidos não pode ser zero")
        return

    nivel = (pedidos_prazo / total_pedidos) * 100

    print(f"Nível de serviço: {nivel:.2f}%")


def tempo_reposicao():

    print("\nTEMPO DE REPOSIÇÃO")

    data_pedido = input("Data do pedido (dd/mm/aaaa): ")
    data_recebimento = input("Data do recebimento (dd/mm/aaaa): ")

    pedido = datetime.strptime(data_pedido, "%d/%m/%7")
    recebimento = datetime.strptime(data_recebimento, "%d/%m/%Y")

    tempo = recebimento - pedido

    print(f"Tempo de reposição: {tempo.days} dias")

def custo_manutencao():

    print("\nCUSTO DE MANUTENÇÃO")

    capital = float(input("Custo de capital: "))
    armazenamento = float(input("Custo de armazenamento: "))
    obsolescencia = float(input("Custo de obsolescência: "))
    seguro = float(input("Custo de seguro: "))

    total = capital + armazenamento + obsolescencia + seguro

    print(f"Custo total de manutenção: R$ {total:.2f}")