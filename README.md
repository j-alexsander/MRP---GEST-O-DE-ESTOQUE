# MRP---GEST-O-DE-ESTOQUE
"""
=============================================================
  SISTEMA DE GESTÃO DE ESTOQUE - SQLite + Python
=============================================================
  Funcionalidades:
    1. Cadastro de Produtos
    2. Registro de Movimentações (Entradas/Saídas)
    3. Consulta em Tempo Real
    4. Alertas Inteligentes
    5. Relatórios Gerenciais (KPIs)
    6. Cadastro de Fornecedores (Expansibilidade)
=============================================================
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional


# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DO BANCO DE DADOS
# ─────────────────────────────────────────────

DB_NAME = "estoque.db"


def conectar() -> sqlite3.Connection:
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row          # Acesso por nome de coluna
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco() -> None:
    """Cria todas as tabelas necessárias caso não existam."""
    with conectar() as conn:
        conn.executescript("""
            -- Fornecedores (expansibilidade futura)
            CREATE TABLE IF NOT EXISTS fornecedores (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT    NOT NULL,
                cnpj        TEXT    UNIQUE,
                contato     TEXT,
                email       TEXT,
                telefone    TEXT,
                criado_em   TEXT    DEFAULT (datetime('now','localtime'))
            );

            -- Produtos
            CREATE TABLE IF NOT EXISTS produtos (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                nome                TEXT    NOT NULL,
                categoria           TEXT    NOT NULL,
                preco_unitario      REAL    NOT NULL CHECK(preco_unitario >= 0),
                quantidade          REAL    NOT NULL DEFAULT 0 CHECK(quantidade >= 0),
                estoque_minimo      REAL    NOT NULL DEFAULT 5,
                especificacoes      TEXT,
                fornecedor_id       INTEGER REFERENCES fornecedores(id) ON DELETE SET NULL,
                criado_em           TEXT    DEFAULT (datetime('now','localtime')),
                atualizado_em       TEXT    DEFAULT (datetime('now','localtime'))
            );

            -- Movimentações
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id      INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
                tipo            TEXT    NOT NULL CHECK(tipo IN (
                                    'compra','devolucao_entrada',
                                    'venda','transferencia','perda'
                                )),
                quantidade      REAL    NOT NULL CHECK(quantidade > 0),
                preco_unitario  REAL,
                custo_total     REAL,
                observacao      TEXT,
                data_pedido     TEXT,
                data_recebimento TEXT,
                registrado_em   TEXT    DEFAULT (datetime('now','localtime'))
            );

            -- Custos de Manutenção do Estoque
            CREATE TABLE IF NOT EXISTS custos_manutencao (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id          INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
                periodo_inicio      TEXT NOT NULL,
                periodo_fim         TEXT NOT NULL,
                custo_capital       REAL DEFAULT 0,
                custo_armazenamento REAL DEFAULT 0,
                custo_obsolescencia REAL DEFAULT 0,
                custo_seguro        REAL DEFAULT 0,
                observacao          TEXT,
                registrado_em       TEXT DEFAULT (datetime('now','localtime'))
            );
        """)
    print("✅  Banco de dados inicializado com sucesso.")


# ─────────────────────────────────────────────
#  VALIDAÇÕES
# ─────────────────────────────────────────────

def validar_numero_positivo(valor, nome: str = "Valor") -> float:
    """Garante que o valor é um número positivo."""
    try:
        v = float(valor)
        if v < 0:
            raise ValueError
        return v
    except (ValueError, TypeError):
        raise ValueError(f"❌  {nome} inválido: deve ser um número positivo.")


def validar_texto(texto, nome: str = "Campo") -> str:
    """Garante que o texto não está vazio."""
    if not str(texto).strip():
        raise ValueError(f"❌  {nome} não pode estar vazio.")
    return str(texto).strip()


def validar_data(texto_data: str, nome: str = "Data") -> str:
    """Valida e retorna data no formato YYYY-MM-DD."""
    try:
        datetime.strptime(texto_data.strip(), "%Y-%m-%d")
        return texto_data.strip()
    except ValueError:
        raise ValueError(f"❌  {nome} inválida. Use o formato YYYY-MM-DD.")


# ─────────────────────────────────────────────
#  1. CADASTRO DE PRODUTOS
# ─────────────────────────────────────────────

def cadastrar_produto(
    nome: str,
    categoria: str,
    preco_unitario: float,
    quantidade: float,
    estoque_minimo: float = 5,
    especificacoes: Optional[str] = None,
    fornecedor_id: Optional[int] = None
) -> int:
    """
    Cadastra um novo produto no banco de dados.

    Parâmetros
    ----------
    nome             : Nome do produto.
    categoria        : Categoria (ex.: 'Eletrônicos').
    preco_unitario   : Preço de venda unitário.
    quantidade       : Quantidade inicial em estoque.
    estoque_minimo   : Limite para disparo de alerta de reposição.
    especificacoes   : Texto livre para especificações técnicas.
    fornecedor_id    : ID do fornecedor (opcional).

    Retorna
    -------
    ID do produto recém-criado.
    """
    nome            = validar_texto(nome, "Nome")
    categoria       = validar_texto(categoria, "Categoria")
    preco_unitario  = validar_numero_positivo(preco_unitario, "Preço")
    quantidade      = validar_numero_positivo(quantidade, "Quantidade")
    estoque_minimo  = validar_numero_positivo(estoque_minimo, "Estoque mínimo")

    with conectar() as conn:
        cursor = conn.execute(
            """
            INSERT INTO produtos
                (nome, categoria, preco_unitario, quantidade,
                 estoque_minimo, especificacoes, fornecedor_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (nome, categoria, preco_unitario, quantidade,
             estoque_minimo, especificacoes, fornecedor_id)
        )
        pid = cursor.lastrowid
    print(f"✅  Produto '{nome}' cadastrado com ID={pid}.")
    return pid


def atualizar_produto(produto_id: int, **campos) -> None:
    """
    Atualiza campos específicos de um produto.

    Exemplo de uso
    --------------
    atualizar_produto(1, preco_unitario=29.90, estoque_minimo=10)
    """
    campos_permitidos = {
        "nome", "categoria", "preco_unitario",
        "estoque_minimo", "especificacoes", "fornecedor_id"
    }
    campos_validos = {k: v for k, v in campos.items() if k in campos_permitidos}
    if not campos_validos:
        raise ValueError("❌  Nenhum campo válido informado para atualização.")

    set_clause = ", ".join(f"{k} = ?" for k in campos_validos)
    set_clause += ", atualizado_em = datetime('now','localtime')"
    valores = list(campos_validos.values()) + [produto_id]

    with conectar() as conn:
        conn.execute(
            f"UPDATE produtos SET {set_clause} WHERE id = ?", valores
        )
    print(f"✅  Produto ID={produto_id} atualizado.")


# ─────────────────────────────────────────────
#  2. REGISTRO DE MOVIMENTAÇÕES
# ─────────────────────────────────────────────

TIPOS_ENTRADA = {"compra", "devolucao_entrada"}
TIPOS_SAIDA   = {"venda", "transferencia", "perda"}


def _ajustar_estoque(conn: sqlite3.Connection, produto_id: int, delta: float) -> float:
    """Aplica variação no estoque e retorna o saldo resultante."""
    cursor = conn.execute(
        "SELECT quantidade FROM produtos WHERE id = ?", (produto_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"❌  Produto ID={produto_id} não encontrado.")

    novo_saldo = row["quantidade"] + delta
    if novo_saldo < 0:
        raise ValueError(
            f"❌  Estoque insuficiente. Saldo atual: {row['quantidade']:.2f}. "
            f"Tentativa de saída: {abs(delta):.2f}."
        )
    conn.execute(
        "UPDATE produtos SET quantidade = ?, atualizado_em = datetime('now','localtime') "
        "WHERE id = ?",
        (novo_saldo, produto_id)
    )
    return novo_saldo


def registrar_entrada(
    produto_id: int,
    tipo: str,
    quantidade: float,
    preco_unitario: Optional[float] = None,
    observacao: Optional[str] = None,
    data_pedido: Optional[str] = None,
    data_recebimento: Optional[str] = None
) -> None:
    """
    Registra uma entrada de estoque.

    Tipos válidos
    -------------
    'compra'            : Compra de fornecedor.
    'devolucao_entrada' : Devolução de cliente.

    Parâmetros
    ----------
    data_pedido      : Data em que o pedido foi realizado (YYYY-MM-DD).
    data_recebimento : Data em que a mercadoria chegou   (YYYY-MM-DD).
    """
    tipo       = validar_texto(tipo, "Tipo").lower()
    quantidade = validar_numero_positivo(quantidade, "Quantidade")

    if tipo not in TIPOS_ENTRADA:
        raise ValueError(f"❌  Tipo de entrada inválido: '{tipo}'. "
                         f"Use: {TIPOS_ENTRADA}.")

    custo_total = None
    if preco_unitario is not None:
        preco_unitario = validar_numero_positivo(preco_unitario, "Preço unitário")
        custo_total    = preco_unitario * quantidade

    if data_pedido:      data_pedido      = validar_data(data_pedido, "Data do pedido")
    if data_recebimento: data_recebimento = validar_data(data_recebimento, "Data de recebimento")

    with conectar() as conn:
        novo_saldo = _ajustar_estoque(conn, produto_id, +quantidade)
        conn.execute(
            """
            INSERT INTO movimentacoes
                (produto_id, tipo, quantidade, preco_unitario, custo_total,
                 observacao, data_pedido, data_recebimento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (produto_id, tipo, quantidade, preco_unitario, custo_total,
             observacao, data_pedido, data_recebimento)
        )
    print(f"✅  Entrada registrada. Produto ID={produto_id} | "
          f"Tipo: {tipo} | Qtd: +{quantidade:.2f} | Saldo: {novo_saldo:.2f}.")


def registrar_saida(
    produto_id: int,
    tipo: str,
    quantidade: float,
    preco_unitario: Optional[float] = None,
    observacao: Optional[str] = None
) -> None:
    """
    Registra uma saída de estoque.

    Tipos válidos
    -------------
    'venda'        : Venda para cliente.
    'transferencia': Transferência para outro local.
    'perda'        : Avaria, extravio, vencimento etc.
    """
    tipo       = validar_texto(tipo, "Tipo").lower()
    quantidade = validar_numero_positivo(quantidade, "Quantidade")

    if tipo not in TIPOS_SAIDA:
        raise ValueError(f"❌  Tipo de saída inválido: '{tipo}'. "
                         f"Use: {TIPOS_SAIDA}.")

    custo_total = None
    if preco_unitario is not None:
        preco_unitario = validar_numero_positivo(preco_unitario, "Preço unitário")
        custo_total    = preco_unitario * quantidade

    with conectar() as conn:
        novo_saldo = _ajustar_estoque(conn, produto_id, -quantidade)
        conn.execute(
            """
            INSERT INTO movimentacoes
                (produto_id, tipo, quantidade, preco_unitario, custo_total, observacao)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (produto_id, tipo, quantidade, preco_unitario, custo_total, observacao)
        )
    print(f"✅  Saída registrada.  Produto ID={produto_id} | "
          f"Tipo: {tipo} | Qtd: -{quantidade:.2f} | Saldo: {novo_saldo:.2f}.")


# ─────────────────────────────────────────────
#  3. CONSULTA EM TEMPO REAL
# ─────────────────────────────────────────────

def consultar_estoque(produto_id: Optional[int] = None) -> list[dict]:
    """
    Retorna o saldo atual de todos os produtos (ou de um produto específico).

    Retorna
    -------
    Lista de dicionários com os dados de cada produto.
    """
    with conectar() as conn:
        if produto_id:
            rows = conn.execute(
                """
                SELECT p.*, f.nome AS fornecedor_nome
                FROM   produtos p
                LEFT JOIN fornecedores f ON f.id = p.fornecedor_id
                WHERE  p.id = ?
                """, (produto_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT p.*, f.nome AS fornecedor_nome
                FROM   produtos p
                LEFT JOIN fornecedores f ON f.id = p.fornecedor_id
                ORDER BY p.categoria, p.nome
                """
            ).fetchall()

    resultado = [dict(r) for r in rows]
    return resultado


def exibir_estoque(produto_id: Optional[int] = None) -> None:
    """Imprime o estoque atual de forma formatada no terminal."""
    produtos = consultar_estoque(produto_id)
    if not produtos:
        print("ℹ️   Nenhum produto encontrado.")
        return

    print("\n" + "═" * 80)
    print(f"{'CONSULTA DE ESTOQUE':^80}")
    print(f"{'Gerado em: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^80}")
    print("═" * 80)
    header = f"{'ID':<5}{'Nome':<25}{'Categoria':<15}{'Preço':>10}{'Qtd':>10}{'Mín.':>8}{'Status':<12}"
    print(header)
    print("─" * 80)

    for p in produtos:
        status = "⚠️  BAIXO" if p["quantidade"] <= p["estoque_minimo"] else "✅  OK"
        print(
            f"{p['id']:<5}"
            f"{p['nome']:<25}"
            f"{p['categoria']:<15}"
            f"R$ {p['preco_unitario']:>7.2f}"
            f"{p['quantidade']:>10.2f}"
            f"{p['estoque_minimo']:>8.2f}"
            f"  {status}"
        )
    print("═" * 80)
    valor_total = sum(p["preco_unitario"] * p["quantidade"] for p in produtos)
    print(f"{'Valor total do estoque:':>60}  R$ {valor_total:>10.2f}")
    print("═" * 80 + "\n")


# ─────────────────────────────────────────────
#  4. ALERTAS INTELIGENTES
# ─────────────────────────────────────────────

def alertas_estoque_baixo() -> list[dict]:
    """
    Retorna produtos cujo estoque atual é menor ou igual ao mínimo configurado.

    Retorna
    -------
    Lista de produtos que precisam de reposição.
    """
    with conectar() as conn:
        rows = conn.execute(
            """
            SELECT id, nome, categoria, quantidade, estoque_minimo,
                   (estoque_minimo - quantidade) AS quantidade_repor
            FROM   produtos
            WHERE  quantidade <= estoque_minimo
            ORDER BY quantidade_repor DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def exibir_alertas() -> None:
    """Exibe notificações de estoque baixo no terminal."""
    alertas = alertas_estoque_baixo()
    print("\n" + "═" * 70)
    print(f"{'⚠️   ALERTAS DE ESTOQUE BAIXO':^70}")
    print("═" * 70)

    if not alertas:
        print("  ✅  Nenhum produto com estoque crítico no momento.")
    else:
        print(f"  {'ID':<5}{'Produto':<25}{'Atual':>8}{'Mínimo':>8}{'Repor':>10}")
        print("  " + "─" * 60)
        for a in alertas:
            print(
                f"  {a['id']:<5}"
                f"{a['nome']:<25}"
                f"{a['quantidade']:>8.2f}"
                f"{a['estoque_minimo']:>8.2f}"
                f"{a['quantidade_repor']:>10.2f}"
            )
    print("═" * 70 + "\n")


# ─────────────────────────────────────────────
#  5. RELATÓRIOS GERENCIAIS / KPIs
# ─────────────────────────────────────────────

def calcular_giro_estoque(
    produto_id: int,
    data_inicio: str,
    data_fim: str
) -> dict:
    """
    Calcula o Giro de Estoque no período informado.

    Fórmula
    -------
    Giro = CMV / Estoque Médio
    Estoque Médio = (Estoque Inicial + Estoque Final) / 2

    Parâmetros
    ----------
    data_inicio : Início do período (YYYY-MM-DD).
    data_fim    : Fim do período   (YYYY-MM-DD).

    Retorna
    -------
    Dicionário com CMV, estoque médio e giro calculado.
    """
    data_inicio = validar_data(data_inicio, "Data início")
    data_fim    = validar_data(data_fim,    "Data fim")

    with conectar() as conn:
        # CMV = soma dos custos das vendas no período
        row_cmv = conn.execute(
            """
            SELECT COALESCE(SUM(custo_total), 0) AS cmv
            FROM   movimentacoes
            WHERE  produto_id = ?
              AND  tipo = 'venda'
              AND  registrado_em BETWEEN ? AND ?
            """,
            (produto_id, data_inicio + " 00:00:00", data_fim + " 23:59:59")
        ).fetchone()

        # Estoque atual (final do período)
        row_est = conn.execute(
            "SELECT quantidade, preco_unitario FROM produtos WHERE id = ?",
            (produto_id,)
        ).fetchone()

    if not row_est:
        raise ValueError(f"❌  Produto ID={produto_id} não encontrado.")

    cmv             = row_cmv["cmv"]
    estoque_final   = row_est["quantidade"] * row_est["preco_unitario"]
    # Simplificação: estoque médio estimado como estoque_final + CMV/2
    estoque_medio   = estoque_final + (cmv / 2)
    giro            = (cmv / estoque_medio) if estoque_medio > 0 else 0

    return {
        "produto_id":     produto_id,
        "periodo":        f"{data_inicio} → {data_fim}",
        "cmv":            cmv,
        "estoque_final":  estoque_final,
        "estoque_medio":  estoque_medio,
        "giro_estoque":   round(giro, 4),
    }


def calcular_nivel_servico(data_inicio: str, data_fim: str) -> dict:
    """
    Calcula o Nível de Serviço no período.

    Fórmula
    -------
    Nível de Serviço (%) = (Pedidos Atendidos / Total de Pedidos) × 100

    Considera 'venda' como pedido; vendas sem flag de perda
    imediatamente posterior são consideradas atendidas.

    Parâmetros
    ----------
    data_inicio : Início do período (YYYY-MM-DD).
    data_fim    : Fim do período   (YYYY-MM-DD).

    Retorna
    -------
    Dicionário com totais e percentual calculado.
    """
    data_inicio = validar_data(data_inicio)
    data_fim    = validar_data(data_fim)

    with conectar() as conn:
        total = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM   movimentacoes
            WHERE  tipo = 'venda'
              AND  registrado_em BETWEEN ? AND ?
            """,
            (data_inicio + " 00:00:00", data_fim + " 23:59:59")
        ).fetchone()["total"]

        # Pedidos não atendidos = perdas no período
        perdas = conn.execute(
            """
            SELECT COUNT(*) AS perdas
            FROM   movimentacoes
            WHERE  tipo = 'perda'
              AND  registrado_em BETWEEN ? AND ?
            """,
            (data_inicio + " 00:00:00", data_fim + " 23:59:59")
        ).fetchone()["perdas"]

    atendidos      = max(total - perdas, 0)
    nivel_servico  = (atendidos / total * 100) if total > 0 else 0

    return {
        "periodo":              f"{data_inicio} → {data_fim}",
        "total_pedidos":        total,
        "pedidos_atendidos":    atendidos,
        "nivel_servico_pct":    round(nivel_servico, 2),
    }


def calcular_tempo_reposicao(produto_id: int) -> dict:
    """
    Calcula o tempo médio de reposição do produto.

    Fórmula
    -------
    Tempo de Reposição = Data de Recebimento − Data do Pedido

    Retorna
    -------
    Dicionário com média, mínimo e máximo de dias para reposição.
    """
    with conectar() as conn:
        rows = conn.execute(
            """
            SELECT data_pedido, data_recebimento
            FROM   movimentacoes
            WHERE  produto_id = ?
              AND  tipo = 'compra'
              AND  data_pedido      IS NOT NULL
              AND  data_recebimento IS NOT NULL
            """,
            (produto_id,)
        ).fetchall()

    if not rows:
        return {
            "produto_id": produto_id,
            "registros":  0,
            "media_dias": None,
            "min_dias":   None,
            "max_dias":   None,
            "mensagem":   "Sem dados de data de pedido/recebimento para este produto.",
        }

    dias = []
    for r in rows:
        try:
            dp = datetime.strptime(r["data_pedido"],      "%Y-%m-%d")
            dr = datetime.strptime(r["data_recebimento"], "%Y-%m-%d")
            dias.append((dr - dp).days)
        except ValueError:
            continue

    return {
        "produto_id": produto_id,
        "registros":  len(dias),
        "media_dias": round(sum(dias) / len(dias), 1) if dias else None,
        "min_dias":   min(dias) if dias else None,
        "max_dias":   max(dias) if dias else None,
    }


def calcular_custo_manutencao(produto_id: int, periodo_inicio: str, periodo_fim: str) -> dict:
    """
    Registra e calcula o custo de manutenção do estoque.

    Fórmula
    -------
    Custo Manutenção = Custo de Capital
                     + Custo de Armazenamento
                     + Custo de Obsolescência
                     + Custo de Seguro

    Parâmetros
    ----------
    produto_id      : ID do produto.
    periodo_inicio  : Início do período (YYYY-MM-DD).
    periodo_fim     : Fim do período   (YYYY-MM-DD).

    Retorna
    -------
    Dicionário com cada componente de custo e o total.
    """
    with conectar() as conn:
        rows = conn.execute(
            """
            SELECT custo_capital, custo_armazenamento,
                   custo_obsolescencia, custo_seguro
            FROM   custos_manutencao
            WHERE  produto_id      = ?
              AND  periodo_inicio >= ?
              AND  periodo_fim    <= ?
            """,
            (produto_id, periodo_inicio, periodo_fim)
        ).fetchall()

    if not rows:
        return {
            "produto_id":           produto_id,
            "custo_capital":        0,
            "custo_armazenamento":  0,
            "custo_obsolescencia":  0,
            "custo_seguro":         0,
            "custo_total":          0,
            "mensagem": "Nenhum lançamento de custo encontrado no período.",
        }

    totais = {
        "custo_capital":        sum(r["custo_capital"]        for r in rows),
        "custo_armazenamento":  sum(r["custo_armazenamento"]  for r in rows),
        "custo_obsolescencia":  sum(r["custo_obsolescencia"]  for r in rows),
        "custo_seguro":         sum(r["custo_seguro"]         for r in rows),
    }
    totais["custo_total"] = sum(totais.values())
    totais["produto_id"]  = produto_id
    return totais


def lancar_custo_manutencao(
    produto_id: int,
    periodo_inicio: str,
    periodo_fim: str,
    custo_capital: float       = 0,
    custo_armazenamento: float = 0,
    custo_obsolescencia: float = 0,
    custo_seguro: float        = 0,
    observacao: Optional[str]  = None
) -> None:
    """Lança um registro de custo de manutenção para o produto."""
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO custos_manutencao
                (produto_id, periodo_inicio, periodo_fim, custo_capital,
                 custo_armazenamento, custo_obsolescencia, custo_seguro, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (produto_id, periodo_inicio, periodo_fim, custo_capital,
             custo_armazenamento, custo_obsolescencia, custo_seguro, observacao)
        )
    print(f"✅  Custo de manutenção lançado para produto ID={produto_id}.")


def relatorio_kpis(produto_id: int, data_inicio: str, data_fim: str) -> None:
    """
    Exibe um relatório consolidado de KPIs para um produto no período.

    Indicadores exibidos
    --------------------
    - Giro de Estoque
    - Nível de Serviço
    - Tempo Médio de Reposição
    - Custo de Manutenção
    """
    print("\n" + "═" * 70)
    print(f"{'📊  RELATÓRIO GERENCIAL DE KPIs':^70}")
    print(f"{'Produto ID: ' + str(produto_id) + ' | ' + data_inicio + ' → ' + data_fim:^70}")
    print("═" * 70)

    # Giro de Estoque
    giro = calcular_giro_estoque(produto_id, data_inicio, data_fim)
    print("\n  📦  GIRO DE ESTOQUE")
    print(f"      CMV (Custo Mercadorias Vendidas) : R$ {giro['cmv']:>10.2f}")
    print(f"      Estoque Médio                    : R$ {giro['estoque_medio']:>10.2f}")
    print(f"      Giro de Estoque                  :    {giro['giro_estoque']:>10.4f}x")

    # Nível de Serviço
    ns = calcular_nivel_servico(data_inicio, data_fim)
    print("\n  🎯  NÍVEL DE SERVIÇO")
    print(f"      Total de Pedidos                 : {ns['total_pedidos']:>12}")
    print(f"      Pedidos Atendidos                : {ns['pedidos_atendidos']:>12}")
    print(f"      Nível de Serviço                 : {ns['nivel_servico_pct']:>11.2f}%")

    # Tempo de Reposição
    tr = calcular_tempo_reposicao(produto_id)
    print("\n  🚚  TEMPO DE REPOSIÇÃO (dias)")
    if tr["media_dias"] is not None:
        print(f"      Média                            : {tr['media_dias']:>10.1f} dias")
        print(f"      Mínimo                           : {tr['min_dias']:>10} dias")
        print(f"      Máximo                           : {tr['max_dias']:>10} dias")
    else:
        print(f"      {tr.get('mensagem', 'Sem dados suficientes.')}")

    # Custo de Manutenção
    cm = calcular_custo_manutencao(produto_id, data_inicio, data_fim)
    print("\n  💰  CUSTO DE MANUTENÇÃO")
    print(f"      Custo de Capital                 : R$ {cm['custo_capital']:>10.2f}")
    print(f"      Custo de Armazenamento           : R$ {cm['custo_armazenamento']:>10.2f}")
    print(f"      Custo de Obsolescência           : R$ {cm['custo_obsolescencia']:>10.2f}")
    print(f"      Custo de Seguro                  : R$ {cm['custo_seguro']:>10.2f}")
    print(f"      ─────────────────────────────────────────────")
    print(f"      TOTAL                            : R$ {cm['custo_total']:>10.2f}")
    print("═" * 70 + "\n")


# ─────────────────────────────────────────────
#  FORNECEDORES (EXPANSIBILIDADE)
# ─────────────────────────────────────────────

def cadastrar_fornecedor(
    nome: str,
    cnpj: Optional[str]     = None,
    contato: Optional[str]  = None,
    email: Optional[str]    = None,
    telefone: Optional[str] = None
) -> int:
    """Cadastra um novo fornecedor."""
    nome = validar_texto(nome, "Nome do fornecedor")
    with conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO fornecedores (nome, cnpj, contato, email, telefone) VALUES (?,?,?,?,?)",
            (nome, cnpj, contato, email, telefone)
        )
        fid = cursor.lastrowid
    print(f"✅  Fornecedor '{nome}' cadastrado com ID={fid}.")
    return fid


def listar_fornecedores() -> list[dict]:
    """Retorna todos os fornecedores cadastrados."""
    with conectar() as conn:
        rows = conn.execute("SELECT * FROM fornecedores ORDER BY nome").fetchall()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
#  INTERFACE DE TEXTO (MENU)
# ─────────────────────────────────────────────

def _input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  Digite um número inteiro válido.")


def _input_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Digite um número válido.")


def menu_principal() -> None:
    """Loop principal da interface de texto."""
    inicializar_banco()
    while True:
        print("""
╔══════════════════════════════════════════╗
║   SISTEMA DE GESTÃO DE ESTOQUE           ║
╠══════════════════════════════════════════╣
║  1. Cadastrar Produto                    ║
║  2. Registrar Entrada                    ║
║  3. Registrar Saída                      ║
║  4. Consultar Estoque                    ║
║  5. Alertas de Estoque Baixo             ║
║  6. Relatório de KPIs                    ║
║  7. Cadastrar Fornecedor                 ║
║  8. Listar Fornecedores                  ║
║  0. Sair                                 ║
╚══════════════════════════════════════════╝""")
        opcao = input("  Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                nome       = input("  Nome do produto   : ")
                categoria  = input("  Categoria         : ")
                preco      = _input_float("  Preço unitário   : R$ ")
                qtd        = _input_float("  Quantidade inicial: ")
                minimo     = _input_float("  Estoque mínimo   : ")
                specs      = input("  Especificações   (Enter para pular): ") or None
                cadastrar_produto(nome, categoria, preco, qtd, minimo, specs)

            elif opcao == "2":
                pid   = _input_int("  ID do produto  : ")
                tipo  = input("  Tipo (compra / devolucao_entrada): ").strip()
                qtd   = _input_float("  Quantidade     : ")
                preco = _input_float("  Preço unitário (0 = não informar): R$ ") or None
                obs   = input("  Observação     (Enter para pular): ") or None
                dp    = input("  Data do pedido     (YYYY-MM-DD, Enter para pular): ") or None
                dr    = input("  Data de recebimento(YYYY-MM-DD, Enter para pular): ") or None
                registrar_entrada(pid, tipo, qtd, preco, obs, dp, dr)

            elif opcao == "3":
                pid   = _input_int("  ID do produto  : ")
                tipo  = input("  Tipo (venda / transferencia / perda): ").strip()
                qtd   = _input_float("  Quantidade     : ")
                preco = _input_float("  Preço unitário (0 = não informar): R$ ") or None
                obs   = input("  Observação     (Enter para pular): ") or None
                registrar_saida(pid, tipo, qtd, preco, obs)

            elif opcao == "4":
                pid = input("  ID do produto (Enter = todos): ").strip()
                exibir_estoque(int(pid) if pid else None)

            elif opcao == "5":
                exibir_alertas()

            elif opcao == "6":
                pid = _input_int("  ID do produto  : ")
                di  = input("  Data início (YYYY-MM-DD): ").strip()
                df  = input("  Data fim    (YYYY-MM-DD): ").strip()
                relatorio_kpis(pid, di, df)

            elif opcao == "7":
                nome     = input("  Nome do fornecedor: ")
                cnpj     = input("  CNPJ   (Enter para pular): ") or None
                contato  = input("  Contato(Enter para pular): ") or None
                email    = input("  E-mail (Enter para pular): ") or None
                telefone = input("  Fone   (Enter para pular): ") or None
                cadastrar_fornecedor(nome, cnpj, contato, email, telefone)

            elif opcao == "8":
                forn = listar_fornecedores()
                if not forn:
                    print("  ℹ️   Nenhum fornecedor cadastrado.")
                else:
                    for f in forn:
                        print(f"  [{f['id']}] {f['nome']} | CNPJ: {f['cnpj']} | {f['email']}")

            elif opcao == "0":
                print("  Saindo... Até logo! 👋")
                break

            else:
                print("  ❌  Opção inválida.")

        except (ValueError, sqlite3.Error) as e:
            print(f"  {e}")


# ─────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    menu_principal()
