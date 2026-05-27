import sqlite3
import os

# Descobre o caminho real da pasta onde o projeto está rodando
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_BANCO = os.path.join(BASE_DIR, "farmacia.db")

def conectar_banco():
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.execute("PRAGMA foreign_keys = ON;")
        return conexao
    except sqlite3.Error as erro:
        print(f"❌ Erro critico ao conectar ao banco de dados: {erro}")
        return None


def inicializar_banco():
    conexao = conectar_banco()
    if conexao is None:
        return
    try:
        cursor = conexao.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            dosagem TEXT,
            preco REAL,
            quantidade INTEGER,
            laboratorio TEXT,
            indicacao TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicamento_id INTEGER,
        tipo TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_total REAL NOT NULL,
        data_movimento DATA DEFAULT (DATE('now', 'localtime')),
        FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
        )
        """)

        conexao.commit()
        print("📊 Banco de dados verificado e tabelas prontas.")

    except sqlite3.Error as erro:
        print(f"❌ Erro ao criar as tabelas: {erro}")
        conexao.rollback()

    finally:
        conexao.close()


def registrar_venda(id_medicamento, quantidade, valor_unitario):
    conexao = conectar_banco()
    if conexao is None:
        return False
    try:
        cursor = conexao.cursor()
        valor_total = quantidade * valor_unitario

        cursor.execute("""
            INSERT INTO movimentacoes (medicamento_id, tipo, quantidade, valor_total)
            VALUES (?, 'VENDA', ?, ?)
        """, (id_medicamento, quantidade, valor_total))

        cursor.execute("UPDATE medicamentos SET quantidade = quantidade - ? WHERE id = ?", (quantidade, id_medicamento))

        conexao.commit()
        print(f"✅ Venda do produto ID {id_medicamento} registrada!")
        return True
    except sqlite3.Error as erro:
        print(f"❌ Erro ao registrar venda: {erro}")
        conexao.rollback()
        return False
    finally:
        conexao.close()

def registrar_reposicao(id_medicamento, quantidade, custo_total):
    conexao = conectar_banco()
    if conexao is None:
        return False
    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO movimentacoes (medicamento_id, tipo, quantidade, valor_total)
            VALUES (?, 'REPOSICAO', ?, ?)
        """, (id_medicamento, quantidade, custo_total))

        cursor.execute("UPDATE medicamentos SET quantidade = quantidade + ? WHERE id = ?", (quantidade, id_medicamento))

        conexao.commit()
        print(f"✅ Reposiçao de produto ID {id_medicamento} registrada!")
        return True
    except sqlite3.Error as erro:
        print(f"❌ Erro ao registrar reposiçao: {erro}")
        conexao.rollback()
        return False
    finally:
        conexao.close()


def buscar_historico_movimentacoes():
    conexao = conectar_banco()
    if conexao is None:
        return []
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT m.tipo, m.quantidade, m.valor_total, m.data_movimento, med.nome, med.dosagem, med.laboratorio
            FROM movimentacoes m
            JOIN medicamentos med ON m.medicamento_id = med.id
            ORDER BY m.id DESC
        """)
        historico = cursor.fetchall()
        return historico
    except sqlite3.Error as erro:
        print(f"❌ Erro ao buscar historico: {erro}")
        return []
    finally:
        conexao.close()

def dados_dashboard_7_dias():
    conexao = conectar_banco()
    if conexao is None:
        return []
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT data_movimento, SUM(valor_total), COUNT(id)
            FROM movimentacoes
            WHERE tipo = 'VENDA'
            GROUP BY data_movimento
            ORDER BY data_movimento DESC
            LIMIT 7
        """)
        dados = cursor.fetchall()
        if not dados:
            return []
        return dados[::-1]
    except sqlite3.Error as erro:
        print(f"❌ Erro ao carregar dashboard: {erro}")
        return  []
    finally:
        conexao.close()

def salvar_produto(nome, dosagem, preco, quantidade, laboratorio, indicacao):

    try:
        preco_formatado = float(preco) if preco is not None else 0.0
    except (ValueError, AttributeError):
        try:
            preco_formatado = float(str(preco).replace(",", ".")) if preco else 0.0
        except ValueError:
            preco_formatado = 0.0

    try:
        quantidade_formatada = int(quantidade) if quantidade else 0
    except ValueError:
        quantidade_formatada = 0

    conexao = conectar_banco()
    if conexao is None:
        print("❌ Nao foi possivel cadastrar porque o banco esta inacessivel.")
        return False
    
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO medicamentos (nome, dosagem, preco, quantidade, laboratorio, indicacao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, dosagem, preco_formatado, quantidade_formatada, laboratorio, indicacao))

        conexao.commit()
        print(f"✅ {nome} cadastro com sucesso!")
        return True
    except sqlite3.Error as erro:
        print(f"❌ Erro ao inserir medicamento no banco: {erro}")
        conexao.rollback()
        return False
    finally:
        conexao.close()


def listar_produtos():
    conexao = conectar_banco()
    if conexao is None:
        return []
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM medicamentos")
        produtos = cursor.fetchall()
        return produtos
    except sqlite3.Error as erro:
        print(f"❌ Erro ao listar medicamentos: {erro}")
        return []
    finally:
        conexao.close()

def deletar_produto(id_produto):
    conexao = conectar_banco()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()
        id_limpo = int(id_produto)
        cursor.execute("DELETE FROM medicamentos WHERE id = ?", (id_limpo,))

        conexao.commit()
        print(f"✅ Produto {id_produto} deletado com sucesso!")
        return True
    except (ValueError, sqlite3.Error) as e:
        print(f"❌ Erro ao deletar produto: {e}")
        conexao.rollback()
        return False
    finally:
        conexao.close()


def atualizar_produto(id_produto, nome, dosagem, preco, quantidade, laboratorio, indicacao):
    try:
        preco_formato = float(str(preco).replace(",",".")) if preco else 0.0
    except ValueError:
        preco_formato = 0.0

    try:
        quandade_formatada = int(quantidade) if quantidade else 0
    except ValueError:
        quandade_formatada = 0

    conexao = conectar_banco()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE medicamentos
            SET nome = ?, dosagem = ?, preco = ?, quantidade = ?, laboratorio = ?, indicacao = ?
            WHERE id = ?
        """, (nome, dosagem, preco_formato, quandade_formatada, laboratorio, indicacao, id_produto))

        conexao.commit()
        print(f"✅ Produto {id_produto} atualizado com sucesso!")
        return True
    except sqlite3.Error as e:
        print(f"❌ Erro ao atualizar o produto no banco: {e}")
        conexao.rollback()
        return False
    finally:
        conexao.close()


def produto_ja_existe(nome, dosagem):
    conexao = conectar_banco()
    if conexao is None:
        return False
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id FROM medicamentos
            WHERE LOWER(nome) = LOWER(?) AND LOWER(dosagem) = LOWER(?)
            """, (nome.strip(), dosagem.strip()))

        resultado = cursor.fetchone()
        return resultado is not None
    except sqlite3.Error as erro:
        print(f"❌ Erro ao verificar existencia do produto: {erro}")
        return False
    finally:
        conexao.close()
