from banco_de_dados import criar_tabelas
from produtos import cadastrar_produto, ver_estoque
from movimentacao import entrada_produto, saida_produto
from relatorio_de_estoque import ver_movimentacoes, giro_estoque, nivel_servico, tempo_reposicao, custo_manutencao
from alertas_de_estoque import verificar_alertas
import time

criar_tabelas()

while True:

    print("""
(1) - Cadastrar Produto
(2) - Ver Estoque
(3 - Entrada De Produto
(4) - Saída De Produto
(5) - Ver Movimentações
(6) - Ver Alertas
(7) - Ver Giro De Estoque
(8) - Nivel de Serviço
(9) - Tempo de Reposição
(10) - Custo de manutenção
(0) - Sair
""")

    opcao = int(input("Escolha: "))

    if opcao == 1:
        cadastrar_produto()

    elif opcao == 2:
        ver_estoque()

    elif opcao == 3:
        entrada_produto()

    elif opcao == 4:
        saida_produto()

    elif opcao == 5:
        ver_movimentacoes()

    elif opcao == 6:
        verificar_alertas()
    elif opcao == 7:
        giro_estoque()
    elif opcao == 8 :
        nivel_servico()
    elif opcao == 9:
        tempo_reposicao()
    elif opcao == 10:
        custo_manutencao()

    elif opcao == 0:
        print("Saindo...")
        time.sleep(2)
        print("Voce Saiu")
        break

    else:
        print("Opção inválida")