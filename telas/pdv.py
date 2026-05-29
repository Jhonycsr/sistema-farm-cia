import sqlite3
import customtkinter as ctk
from customtkinter import CTkLabel
from funcoes.BancoDeDados import conectar_banco


class TelaPDV(ctk.CTkFrame):
    def __init__(self, master, funcionario, **kwargs):
        self.funcionario_atual = funcionario
        super().__init__(master, fg_color="transparent", **kwargs)

        # Título da Tela
        label_titulo = ctk.CTkLabel(self, text="Ponto de Venda (PDV)", font=("Arial", 24, "bold"))
        label_titulo.pack(pady=(0, 20), anchor="w")
        
        # Container Principal
        self.container_pdv = ctk.CTkFrame(self, fg_color="transparent")
        self.container_pdv.pack(fill="both", expand=True)

        self.frame_esquerda = ctk.CTkFrame(self.container_pdv, fg_color="transparent")
        self.frame_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Card de Inputs
        self.frame_inputs = ctk.CTkFrame(self.frame_esquerda, fg_color="#141414", corner_radius=12, border_width=1,
                                         border_color="#2b2b2b")
        self.frame_inputs.pack(fill="x", pady=(0, 15), padx=2, ipady=10)

        ctk.CTkLabel(self.frame_inputs, text="📦 Lançamento de Medicamentos", font=("Arial", 14, "bold"),
                     text_color="#00adb5").pack(pady=(10, 5), padx=15, anchor="w")

        # Campo: Buscar Produto
        self.lbl_busca = ctk.CTkLabel(self.frame_inputs, text="Digite o Nome ou Código do Medicamento:",
                                      font=("Arial", 12), text_color="#aaa")
        self.lbl_busca.pack(padx=15, anchor="w", pady=(5, 0))

        self.ent_busca_prod = ctk.CTkEntry(self.frame_inputs, placeholder_text="Ex: Amoxicilina ou digite o ID...",
                                           height=35, font=("Arial", 14))
        self.ent_busca_prod.pack(fill="x", padx=15, pady=5)

        self.frame_qtd_preco = ctk.CTkFrame(self.frame_inputs, fg_color="transparent")
        self.frame_qtd_preco.pack(fill="x", padx=15, pady=5)

        self.frame_qtd = ctk.CTkFrame(self.frame_qtd_preco, fg_color="transparent")
        self.frame_qtd.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkLabel(self.frame_qtd, text="Quantidade:", font=("Arial", 11), text_color="#aaa").pack(anchor="w")
        self.ent_qtd = ctk.CTkEntry(self.frame_qtd, height=30, placeholder_text="1")
        self.ent_qtd.insert(0, "1")
        self.ent_qtd.pack(fill="x", pady=2)

        # Botão Adicionar Item
        self.btn_adicionar = ctk.CTkButton(self.frame_inputs, text="➕ Adicionar Item (Enter)", fg_color="#1f538d",
                                           hover_color="#2a6ca6", height=35, font=("Arial", 12, "bold"))
        self.btn_adicionar.pack(fill="x", padx=15, pady=(10, 5))

        # Tabela / Cupom Fiscal do lado esquerdo
        self.frame_tabela_container = ctk.CTkFrame(self.frame_esquerda, fg_color="#141414", corner_radius=12,
                                                   border_width=1, border_color="#2b2b2b")
        self.frame_tabela_container.pack(fill="both", expand=True, padx=2)

        ctk.CTkLabel(self.frame_tabela_container, text="🛒 Itens do Cupom Atual", font=("Arial", 14, "bold"),
                     text_color="#00adb5").pack(pady=10, padx=15, anchor="w")

        self.scroll_itens = ctk.CTkScrollableFrame(self.frame_tabela_container, fg_color="transparent")
        self.scroll_itens.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.frame_direita = ctk.CTkFrame(self.container_pdv, width=320, fg_color="#141414", corner_radius=12,
                                          border_width=1, border_color="#2b2b2b")
        self.frame_direita.pack(side="right", fill="both", padx=(10, 0))
        self.frame_direita.pack_propagate(False)

        # Card de Totalizador
        self.frame_total = ctk.CTkFrame(self.frame_direita, fg_color="#1a1a1a", corner_radius=8, border_width=1,
                                        border_color="#222")
        self.frame_total.pack(fill="x", padx=15, pady=20)

        ctk.CTkLabel(self.frame_total, text="TOTAL A PAGAR", font=("Arial", 12, "bold"), text_color="#aaa").pack(
            pady=(15, 0))
        self.lbl_total_geral = ctk.CTkLabel(self.frame_total, text="R$ 0,00", font=("Arial", 26, "bold"),
                                            text_color="#2a944d", wraplength=280)
        self.lbl_total_geral.pack(pady=(5, 15))

        # Seletor de Forma de Pagamento
        ctk.CTkLabel(self.frame_direita, text="Forma de Pagamento:", font=("Arial", 13, "bold"),
                     text_color="#00adb5").pack(padx=15, anchor="w", pady=(10, 5))

        self.var_pagamento = ctk.StringVar(value="DINHEIRO")

        self.rad_dinheiro = ctk.CTkRadioButton(self.frame_direita, text="💵 Dinheiro", variable=self.var_pagamento,
                                               value="DINHEIRO")
        self.rad_dinheiro.pack(padx=20, pady=5, anchor="w")

        self.rad_cartao = ctk.CTkRadioButton(self.frame_direita, text="💳 Cartão de Crédito/Débito",
                                             variable=self.var_pagamento, value="CARTAO")
        self.rad_cartao.pack(padx=20, pady=5, anchor="w")

        self.rad_pix = ctk.CTkRadioButton(self.frame_direita, text="⚡ PIX", variable=self.var_pagamento, value="PIX")
        self.rad_pix.pack(padx=20, pady=5, anchor="w")

        # Espaçador dinâmico
        self.frame_espaco = ctk.CTkFrame(self.frame_direita, fg_color="transparent")
        self.frame_espaco.pack(fill="both", expand=True)

        # Botão de Cancelar Compra Inteira
        self.btn_cancelar_tudo = ctk.CTkButton(
            self.frame_direita,
            text="🗑️ CANCELAR COMPRA",
            fg_color="transparent",
            hover_color="#942a2a",
            text_color="#ef4444",
            border_width=1,
            border_color="#942a2a",
            height=35,
            font=("Arial", 12, "bold")
        )
        self.btn_cancelar_tudo.pack(fill="x", padx=15, pady=(0, 5))


        # Botão de Confirmar Venda
        self.btn_confirmar_venda = ctk.CTkButton(
            self.frame_direita,
            text="🎯 FINALIZAR VENDA (F10)",
            fg_color="#2a944d",
            hover_color="#1f6e39",
            height=50,
            font=("Arial", 16, "bold")
        )
        self.btn_confirmar_venda.pack(fill="x", padx=15, pady=20)

        self.carrinho_atual = []
        self.configurar_eventos()

    def configurar_eventos(self):
        """Vincula os botões e teclas de atalho às funções corretas."""
        self.btn_adicionar.configure(command=self.adicionar_item_carrinho)
        self.btn_confirmar_venda.configure(command=self.finalizar_venda)
        self.btn_cancelar_tudo.configure(command=self.cancelar_compra_inteira)
        self.ent_busca_prod.bind("<Return>", lambda event: self.adicionar_item_carrinho())


    def remover_item_especifico(self, index):
        if 0 <= index < len(self.carrinho_atual):
            self.carrinho_atual.pop(index)
            self.atualizar_visual_carrinho()


    def cancelar_compra_inteira(self):
        if not self.carrinho_atual:
            return

        self.carrinho_atual.clear()
        self.atualizar_visual_carrinho()
        self.lbl_total_geral.configure(text="Compra Cancelada", text_color="#aaa")


    def adicionar_item_carrinho(self):
        """Busca o medicamento no banco e joga na lista em memória."""
        termo = self.ent_busca_prod.get().strip()
        qtd_texto = self.ent_qtd.get().strip()

        if not termo:
            return

        try:
            quantidade = int(qtd_texto)
            if quantidade <= 0: raise ValueError
        except ValueError:
            self.lbl_total_geral.configure(text="Qtd Inválida", text_color="#942a2a")
            return

        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, dosagem, preco, quantidade, laboratorio
            FROM medicamentos
            WHERE id = ?
            OR LOWER(nome) LIKE LOWER(?)
        """, (termo, f"%{termo}%")
        )

        medicamento = cursor.fetchone()
        conn.close()

        if not medicamento:
            self.lbl_total_geral.configure(text="Não Encontrado", text_color="#942a2a")
            return

        m_id, nome, dosagem, preco, qtd_estoque, lab = medicamento

        if qtd_estoque < quantidade:
            self.lbl_total_geral.configure(text="Sem Estoque", text_color="#942a2a")
            return

        subtotal = preco * quantidade

        self.carrinho_atual.append({
            "id": m_id,
            "nome": nome,
            "dosagem": dosagem,
            "lab": lab,
            "qtd": quantidade,
            "preco": preco,
            "subtotal": subtotal
        })

        self.ent_busca_prod.delete(0, "end")
        self.ent_qtd.delete(0, "end")
        self.ent_qtd.insert(0, "1")

        self.atualizar_visual_carrinho()

    def atualizar_visual_carrinho(self):
        """Redesenha a lista de itens na tela e recalcula o valor total."""
        for w in self.scroll_itens.winfo_children():
            w.destroy()

        total_geral = 0.0

        for idx, item in enumerate(self.carrinho_atual):
            total_geral += item["subtotal"]

            linha = ctk.CTkFrame(self.scroll_itens, fg_color="#1a1a1a", corner_radius=6, border_width=1,
                                 border_color="#262626")
            linha.pack(fill="x", pady=4, padx=5)

            btn_remover_item = ctk.CTkButton(
                linha,
                text="❌",
                width=28,
                height=24,
                fg_color="transparent",
                hover_color="#942a2a",
                text_color="#ef4444",
                font=("Arial", 10, "bold"),
                command=lambda i=idx: self.remover_item_especifico(i)
            )
            btn_remover_item.pack(side="left", padx=(5, 2))

            texto_prod = f"{item['nome']} ({item['dosagem']}) x{item['qtd']}"
            ctk.CTkLabel(linha, text=texto_prod, font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=10, pady=8)
            valor_formatated = f"R$ {item['subtotal']:,.2f}".replace(".", ",")
            ctk.CTkLabel(linha, text=valor_formatated, font=("Arial", 12), text_color="#00adb5").pack(side="right", padx=10)

        total_texto = f"R$ {total_geral:,.2f}".replace(".", ",")
        self.lbl_total_geral.configure(text=total_texto, text_color="#2a944d")

    def finalizar_venda(self):
        """Grava a venda no histórico e abate a quantidade de cada medicamento passado."""
        if not self.carrinho_atual:
            return

        conn = conectar_banco()
        cursor = conn.cursor()

        try:
            for item in self.carrinho_atual:
                cursor.execute("""
                    UPDATE medicamentos
                    SET quantidade = quantidade - ?
                    WHERE id = ?
                """, (item["qtd"], item["id"])
                )

                cursor.execute("""
                    INSERT INTO movimentacoes (medicamento_id, tipo, quantidade, valor_total, usuario)
                    VALUES (?, ?, ?, ?, ?)
                    """, (item["id"], "VENDA", item["qtd"], item["subtotal"], self.funcionario_atual)
                    )

            conn.commit()
            self.carrinho_atual.clear()
            self.atualizar_visual_carrinho()
            self.lbl_total_geral.configure(text="Venda Concluída!", text_color="#00adb5")

        except Exception as e:
            conn.rollback()
            self.lbl_total_geral.configure(text="Erro ao Salvar", text_color="#942a2a")
            print(f"Erro no PDV: {e}")
        finally:
            conn.close()
