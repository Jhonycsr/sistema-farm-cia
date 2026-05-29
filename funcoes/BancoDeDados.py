import sqlite3
import os
import hashlib


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
        usuario TEXT,
        FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
        )
        """)

        conexao.commit()
        try:
            cursor.execute("ALTER TABLE movimentacoes ADD COLUMN usuario TEXT DEFAULT 'Sistema';")
            conexao.commit()
        except sqlite3.OperationalError:
            pass

        print("📊 Banco de dados verificado e tabelas prontas.")

    except sqlite3.Error as erro:
        print(f"❌ Erro ao criar as tabelas: {erro}")
        conexao.rollback()

    finally:
        conexao.close()


def registrar_venda(id_medicamento, quantidade, valor_unitario, usuario):
    conexao = conectar_banco()
    if conexao is None:
        return False
    try:
        cursor = conexao.cursor()
        valor_total = quantidade * valor_unitario

        cursor.execute("""
            INSERT INTO movimentacoes (medicamento_id, tipo, quantidade, valor_total, usuario)
            VALUES (?, 'VENDA', ?, ?, ?)
        """, (id_medicamento, quantidade, valor_total, usuario))

        cursor.execute("UPDATE medicamentos SET quantidade = quantidade - ? WHERE id = ?", (quantidade, id_medicamento))

        conexao.commit()
        print(f"✅ Venda do produto ID {id_medicamento} registrada por {usuario}!")
        return True
    except sqlite3.Error as erro:
        print(f"❌ Erro ao registrar venda: {erro}")
        conexao.rollback()
        return False
    finally:
        conexao.close()

def registrar_reposicao(id_medicamento, quantidade, custo_total, usuario):
    conexao = conectar_banco()
    if conexao is None:
        return False
    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO movimentacoes (medicamento_id, tipo, quantidade, valor_total, usuario)
            VALUES (?, 'REPOSICAO', ?, ?, ?)
        """, (id_medicamento, quantidade, custo_total, usuario))

        cursor.execute("UPDATE medicamentos SET quantidade = quantidade + ? WHERE id = ?", (quantidade, id_medicamento))

        conexao.commit()
        print(f"✅ Reposição de produto ID {id_medicamento} registrada por {usuario}!")
        return True
    except sqlite3.Error as erro:
        print(f"❌ Erro ao registrar reposição: {erro}")
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
            SELECT m.tipo, m.quantidade, m.valor_total, m.data_movimento, med.nome, med.dosagem, med.laboratorio, m.usuario
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


def contar_estoque_critico(limite=5):
    conexao = conectar_banco()
    if conexao is None:
        return 0
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(id) FROM medicamentos WHERE quantidade <= ?", (limite,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado[0] else 0
    except sqlite3.Error as erro:
        print(f"❌ Erro ao contar estoque critico: {erro}")
        return 0
    finally:
        conexao.close()


def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def criar_tabela_usuarios():
    conexao = conectar_banco()
    if conexao is None:
        return
    try:
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nivel TEXT NOT NULL -- 'ADMINISTRADOR' ou 'ATENDENTE'
            )
            """)
        conexao.commit()

        cursor.execute("SELECT COUNT(id) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            senha_adimin_hash = gerar_hash_senha("admin123")
            cursor.execute("""
                INSERT INTO usuarios (usuario, senha, nivel)
                VALUES ('admin', ?, 'ADMINISTRADOR')
                """, (senha_adimin_hash,))
            conexao.commit()
            print("👤 Usuario administrador padrao ('admin' / 'admin123') criado com sucesso!")

        cursor.execute("SELECT COUNT(id) FROM usuarios WHERE usuario = 'user'")
        if cursor.fetchone()[0] == 0:
            senha_atendente_hash = gerar_hash_senha("user123")
            cursor.execute("""
                INSERT INTO usuarios (usuario, senha, nivel)
                VALUES ('user', ?, 'ATENDENTE')
                """, (senha_atendente_hash,))
            conexao.commit()
            print("👥 Usuario atendente padrao ('user' / 'user123') criado com sucesso!")

    except sqlite3.Error as e:
        print(f"❌ Erro ao criar tabela usuaruis: {e}")
    finally:
        conexao.close()



def verificar_credenciais(usuario, senha_digitada):
    conexao = conectar_banco()
    if conexao is None:
        return None
    try:
        cursor = conexao.cursor()

        senha_hash = gerar_hash_senha(senha_digitada)

        cursor.execute("""
            SELECT nivel FROM usuarios
            WHERE usuario = ? AND senha = ?
        """, (usuario, senha_hash))

        resultado = cursor.fetchone()

        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"❌ Erro ao verificar credenciais: {e}")
        return None
    finally:
        conexao.close()


def listar_usuarios():
    conexao = conectar_banco()
    if conexao is None:
        return []
    try:
        cursor = conexao.cursor()

        cursor.execute("SELECT id, usuario, nivel FROM usuarios ORDER BY usuario ASC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ Erro ao listar usuarios: {e}")
        return []
    finally:
        conexao.close()


def excluir_usuario(id_usuario):
    conexao = conectar_banco()
    if conexao is None:
        return False
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
        conexao.commit()
        return True
    except sqlite3.Error as e:
        print(f"❌ Erro ao excluir usuario: {e}")
        return False
    finally:
        conexao.close()


def cadastrar_novo_usuario(usuario, senha_pura, nivel):
    conexao = conectar_banco()
    if conexao is None:
        return False, "Erro de conexao com o banco."
    try:
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario.lower(),))
        if cursor.fetchone():
            return False, "Este nome de usuario ja esta em uso!"

        senha_hash = gerar_hash_senha(senha_pura)

        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, nivel)
            VALUES (?, ?, ?)
        """, (usuario.lower(), senha_hash, nivel))
        conexao.commit()
        return True, "Usuario cadastrado com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro no banco de dados: {e}"
    finally:
        conexao.close()
