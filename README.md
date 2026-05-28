# 📦 Sistema de Gestão de Estoque

**Controle completo de inventário via terminal — do cadastro ao giro de estoque.**

## 📋 Sobre o Projeto

Sistema de gestão de estoque desenvolvido em **Python 3**, com interface interativa de menu via terminal (CLI). Pensado para pequenas e médias empresas que precisam de controle total sobre seu inventário — sem precisar de banco de dados ou dependências externas.

O sistema cobre todo o ciclo de vida do estoque: cadastro de produtos, registro de entradas e saídas, acompanhamento de movimentações, alertas de reabastecimento e indicadores de desempenho (KPIs).

---

## 🚀 Funcionalidades

| # | Módulo | Descrição |
|:-:|--------|-----------|
| `1` | **Cadastrar Produto** | Registra novos produtos com código, nome, categoria, quantidade inicial e custo unitário |
| `2` | **Ver Estoque** | Exibe o inventário completo com quantidades e valores em tempo real |
| `3` | **Entrada de Produto** | Registra entradas de mercadoria com data, quantidade e fornecedor |
| `4` | **Saída de Produto** | Registra saídas e atualiza o saldo automaticamente |
| `5` | **Ver Movimentações** | Histórico completo de todas as entradas e saídas por produto ou período |
| `6` | **Ver Alertas** | Notifica produtos que atingiram ou ultrapassaram o estoque mínimo configurado |
| `7` | **Giro de Estoque** | Calcula a taxa de rotatividade de cada produto no período |
| `8` | **Nível de Serviço** | KPI que mede a disponibilidade e o atendimento à demanda |
| `9` | **Tempo de Reposição** | Estima o lead time necessário para reabastecimento de cada item |
| `10` | **Custo de Manutenção** | Calcula o custo financeiro de manter o estoque atual armazenado |
| `0` | **Sair** | Encerra o sistema |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- Orientação a Objetos (POO)
- Estruturas de dados nativas: `list`, `dict`
- Módulos padrão: `datetime`, `os`, `json`
- Interface de menu interativa via terminal

> Sem dependências externas. Basta ter o Python instalado.

---

## ▶️ Como Executar

### Pré-requisitos

- Python 3.8 ou superior instalado
- Terminal (CMD, PowerShell, Bash, etc.)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/gestao-estoque.git

# 2. Acesse a pasta do projeto
cd gestao-estoque

# 3. Execute o sistema
python main.py
```

### Navegação no Menu

```
============================================
       SISTEMA DE GESTÃO DE ESTOQUE        
============================================

 (1)  - Cadastrar Produto
 (2)  - Ver Estoque
 (3)  - Entrada De Produto
 (4)  - Saída De Produto
 (5)  - Ver Movimentações
 (6)  - Ver Alertas
 (7)  - Ver Giro De Estoque
 (8)  - Nível de Serviço
 (9)  - Tempo de Reposição
 (10) - Custo de Manutenção
 (0)  - Sair

 Escolha uma opção: _
```

---

## 📁 Estrutura do Projeto

```
gestao-estoque/
│
├── main.py                 # Ponto de entrada — exibe o menu principal
├── produto.py              # Classe Produto
├── estoque.py              # Classe Estoque — lógica central
├── movimentacao.py         # Classe Movimentacao (entradas/saídas)
├── relatorios.py           # Giro, Nível de Serviço, Alertas e KPIs
├── dados/
│   ├── produtos.json       # Persistência dos produtos cadastrados
│   └── movimentacoes.json  # Histórico de movimentações
└── README.md
```

---

## 📊 Indicadores e Cálculos

### Giro de Estoque
```
Giro = Saídas no Período / Estoque Médio
```
Indica quantas vezes o estoque foi renovado em um dado período. Quanto maior, mais eficiente.

### Nível de Serviço
```
Nível de Serviço (%) = (Pedidos Atendidos / Pedidos Solicitados) × 100
```
Mede a capacidade de atender a demanda sem rupturas de estoque.

### Ponto de Reposição
```
Ponto de Reposição = Demanda Média Diária × Tempo de Reposição (dias)
```
Define o momento ideal para solicitar um novo pedido ao fornecedor.

### Custo de Manutenção
```
Custo = Estoque Médio × Custo Unitário × Taxa de Manutenção (%)
```
Representa o custo financeiro de manter os itens armazenados.

---

## 🔔 Sistema de Alertas

O sistema verifica automaticamente os produtos com estoque abaixo do mínimo configurado e exibe notificações ao acessar o menu **Alertas (opção 6)**:

```
⚠️  ALERTAS DE ESTOQUE CRÍTICO
─────────────────────────────────────────
 Produto        | Estoque Atual | Mínimo
─────────────────────────────────────────
 Parafuso M5    |      8        |   20
 Cola Epóxi     |      2        |   10
─────────────────────────────────────────
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um **fork** do projeto
2. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
3. Commit suas alterações: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um **Pull Request**

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

Desenvolvido com 🐍 Python

</div>
