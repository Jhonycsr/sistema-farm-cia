import customtkinter as ctk
from funcoes.BancoDeDados import listar_produtos, deletar_produto, atualizar_produto, registrar_reposicao


class TelaListagem(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Título da Tela
        label_titulo = ctk.CTkLabel(self, text="Lista de Estoque", font=("Arial", 24, "bold"))
        label_titulo.pack(pady=(0, 20), anchor="w", padx=40)

        # Container rolável principalizado no centro
        self.container_tabela = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container_tabela.pack(fill="both", expand=True, padx=40, pady=10)

        self.carregar_tabela()

    def carregar_tabela(self):
        for widget in self.container_tabela.winfo_children():
            widget.destroy()

        larguras = {
            "medicamento": 200,
            "dosagem": 100,
            "preco": 100,
            "qtd": 90,
            "laboratorio": 140,
            "acoes": 130
        }

        # --- CABEÇALHO ---
        frame_cabecalho = ctk.CTkFrame(self.container_tabela, fg_color="transparent", height=35)
        frame_cabecalho.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(frame_cabecalho, text="Medicamento", width=larguras["medicamento"], font=("Arial", 13, "bold"),
                     text_color="#1f538d", anchor="w").pack(side="left")
        ctk.CTkLabel(frame_cabecalho, text="Dosagem", width=larguras["dosagem"], font=("Arial", 13, "bold"),
                     text_color="#1f538d", anchor="center").pack(side="left")
        ctk.CTkLabel(frame_cabecalho, text="Preço", width=larguras["preco"], font=("Arial", 13, "bold"),
                     text_color="#1f538d", anchor="center").pack(side="left")
        ctk.CTkLabel(frame_cabecalho, text="Qtd", width=larguras["qtd"], font=("Arial", 13, "bold"),
                     text_color="#1f538d", anchor="center").pack(side="left")
        ctk.CTkLabel(frame_cabecalho, text="Laboratório", width=larguras["laboratorio"], font=("Arial", 13, "bold"),
                     text_color="#1f538d", anchor="center").pack(side="left")
        ctk.CTkLabel(frame_cabecalho, text="Ações", width=larguras["acoes"], font=("Arial", 13, "bold"),
                     text_color="#1f538d", anchor="center").pack(side="left")

        try:
            produtos = listar_produtos()
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            produtos = []

        if not produtos:
            lbl_vazio = ctk.CTkLabel(self.container_tabela, text="Nenhum produto cadastrado no estoque.",
                                     font=("Arial", 14))
            lbl_vazio.pack(pady=40)
            return

        # --- LINHAS DE DADOS ---
        for prod in produtos:
            id_banco = prod[0]
            nome = prod[1]
            dosagem = prod[2]
            preco = prod[3]
            quantidade = prod[4]
            laboratorio = prod[5]
            indicacao = prod[6] if len(prod) == 7 else "Nenhuma indicação informada."

            preco_formatado = f"R$ {preco:,.2f}".replace(".", ",")

            es_critico = quantidade < 5

            cor_borda = "#942a2a" if es_critico else "#222"
            largura_borda = 1 if es_critico else 0
            cor_texto_qtd = "#ff4a4a" if es_critico else "white"
            nome_exibicao = f"⚠️ {nome}" if es_critico else str(nome)

            linha_frame = ctk.CTkFrame(self.container_tabela, fg_color="#1e1e1e", height=45, corner_radius=6,
                                       border_width=largura_borda, border_color=cor_borda)
            linha_frame.pack(fill="x", padx=5, pady=4)
            linha_frame.pack_propagate(False)

            frame_nome_bloco = ctk.CTkFrame(linha_frame, fg_color="transparent", width=larguras["medicamento"])
            frame_nome_bloco.pack(side="left", fill="y")
            frame_nome_bloco.pack_propagate(False)

            frame_desc = ctk.CTkFrame(self.container_tabela, fg_color="#141414", corner_radius=5)
            lbl_desc = ctk.CTkLabel(frame_desc, text=f"📋 Indicação:\n{indicacao}", text_color="#aaa", justify="left",
                                    anchor="w")
            lbl_desc.pack(padx=15, pady=10, fill="x")

            btn_seta = ctk.CTkButton(frame_nome_bloco, text="▶", width=20, height=20, fg_color="transparent",
                                     text_color="#1f538d", font=("Arial", 11, "bold"))
            btn_seta.pack(side="left", padx=(10, 5))
            btn_seta.configure(command=lambda b=btn_seta, f=frame_desc: self.alternar_descricao(b, f))

            ctk.CTkLabel(frame_nome_bloco, text=nome_exibicao, font=("Arial", 13, "bold"), anchor="w").pack(side="left",
                                                                                                            fill="x",
                                                                                                            expand=True),            ctk.CTkLabel(linha_frame, text=str(dosagem), width=larguras["dosagem"], font=("Arial", 13),
                         anchor="center").pack(side="left")
            ctk.CTkLabel(linha_frame, text=preco_formatado, width=larguras["preco"], font=("Arial", 13),
                         anchor="center").pack(side="left")
            ctk.CTkLabel(linha_frame, text=str(quantidade), width=larguras["qtd"], font=("Arial", 13, "bold"),
                         text_color=cor_texto_qtd, anchor="center").pack(side="left")
            ctk.CTkLabel(linha_frame, text=str(laboratorio), width=larguras["laboratorio"], font=("Arial", 13),
                         anchor="center").pack(side="left")

            # Bloco Lateral de Botões de Ações
            frame_acoes = ctk.CTkFrame(linha_frame, fg_color="transparent", width=larguras["acoes"])
            frame_acoes.pack(side="left", fill="y")
            frame_acoes.pack_propagate(False)

            # Botão Repor Estoque
            btn_repor = ctk.CTkButton(
                frame_acoes, text="📦 Repor", width=60, height=26, fg_color="#1f538d", hover_color="#14375a",
                command=lambda id_p=id_banco, n=nome, q=quantidade, p=preco: self.abrir_popup_reposicao(id_p, n, q, p)
            )
            btn_repor.pack(side="left", padx=2, pady=9)

            # Botão Editar
            btn_editar = ctk.CTkButton(
                frame_acoes, text="✏️", width=30, height=26, fg_color="#2b2b2b", hover_color="#1f538d",
                command=lambda id_p=id_banco, p=prod: self.abrir_popup_editar(id_p, p)
            )
            btn_editar.pack(side="left", padx=2, pady=9)

            # Botão Excluir
            btn_excluir = ctk.CTkButton(
                frame_acoes, text="🗑️", width=30, height=26, fg_color="#2b2b2b", hover_color="#942a2a",
                command=lambda id_p=id_banco: self.acao_excluir(id_p)
            )
            btn_excluir.pack(side="left", padx=2, pady=9)

            frame_desc.linha_associada = interception_frame = linha_frame

    def alternar_descricao(self, botao, frame_desc):
        if botao.cget("text") == "▶":
            botao.configure(text="▼")
            frame_desc.pack(after=frame_desc.linha_associada, fill="x", padx=(45, 15), pady=(2, 6))
        else:
            botao.configure(text="▶")
            frame_desc.pack_forget()

    def acao_excluir(self, id_produto):
        deletar_produto(int(id_produto))
        self.carregar_tabela()

    def abrir_popup_reposicao(self, id_produto, nome_produto, qtd_atual, preco_unitario):
        popup = ctk.CTkToplevel(self)
        popup.title("Repor Estoque")
        popup.geometry("320x210")
        popup.resizable(False, False)

        popup.withdraw()
        popup.update_idletasks()
        popup.deiconify()
        popup.grab_set()
        popup.focus_set()

        ctk.CTkLabel(popup, text=f"Repor: {nome_produto}", font=("Arial", 14, "bold"), text_color="#1f538d").pack(
            pady=(15, 5), padx=20, anchor="w")
        ctk.CTkLabel(popup, text=f"Estoque Atual: {qtd_atual} unidades", text_color="#aaa", font=("Arial", 12)).pack(
            padx=20, anchor="w")

        txt_qtd = ctk.CTkEntry(popup, width=280)
        txt_qtd.insert(0, "1")
        txt_qtd.pack(padx=20, pady=5)
        txt_qtd.focus()

        lbl_status = ctk.CTkLabel(popup, text="", font=("Arial", 12, "bold"))
        lbl_status.pack(pady=(5, 0))

        def confirmar_reposicao():
            try:
                qtd_entrada = int(txt_qtd.get())
                if qtd_entrada <= 0: raise ValueError
            except ValueError:
                qtd_entrada = 1

            usuario_ativo = getattr(self.master, 'usuario_atual', 'Sistema')

            registrar_reposicao(id_produto, qtd_entrada, (qtd_entrada * preco_unitario), usuario_ativo)

            lbl_status.configure(text="✅ Entrada registrada com sucesso!", text_color="#2a944d")
            popup.after(1000, lambda: [popup.destroy(), self.carregar_tabela()])

        ctk.CTkButton(popup, text="Confirmar Entrada", fg_color="#1f538d", hover_color="#14375e",
                      command=confirmar_reposicao).pack(pady=10, padx=20, fill="x")

    def abrir_popup_editar(self, id_produto, dados_produto):
        popup = ctk.CTkToplevel(self)
        popup.title("Editar Produto")
        popup.geometry("400x590")
        popup.resizable(False, False)

        popup.withdraw()
        popup.update_idletasks()
        popup.deiconify()
        popup.grab_set()
        popup.focus_set()

        id_banco, nome, dosagem, preco, quantidade, laboratorio = dados_produto[:6]
        indicacao = dados_produto[6] if len(dados_produto) == 7 else "Nenhuma indicação informada."

        ctk.CTkLabel(popup, text="Nome do Medicamento:").pack(pady=(15, 0), padx=20, anchor="w")
        txt_nome = ctk.CTkEntry(popup, width=350)
        txt_nome.insert(0, str(nome))
        txt_nome.pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Dosagem:").pack(pady=(10, 0), padx=20, anchor="w")
        txt_dosagem = ctk.CTkEntry(popup, width=350)
        txt_dosagem.insert(0, str(dosagem))
        txt_dosagem.pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Preço:").pack(pady=(10, 0), padx=20, anchor="w")
        txt_preco = ctk.CTkEntry(popup, width=350)
        txt_preco.insert(0, str(preco))
        txt_preco.pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Quantidade:").pack(pady=(10, 0), padx=20, anchor="w")
        txt_qtd = ctk.CTkEntry(popup, width=350)
        txt_qtd.insert(0, str(quantidade))
        txt_qtd.pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Laboratório:").pack(pady=(10, 0), padx=20, anchor="w")
        txt_lab = ctk.CTkEntry(popup, width=350)
        txt_lab.insert(0, str(laboratorio))
        txt_lab.pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Indicação:").pack(pady=(10, 0), padx=20, anchor="w")
        txt_indicacao = ctk.CTkTextbox(popup, width=350, height=70, corner_radius=5)
        txt_indicacao.insert("1.0", str(indicacao))
        txt_indicacao.pack(padx=20, pady=5)

        lbl_status = ctk.CTkLabel(popup, text="", font=("Arial", 12, "bold"))
        lbl_status.pack(pady=(2, 0))

        def salvar_alteracoes():
            try:
                p_fmt = float(str(txt_preco.get()).replace(",", "."))
            except ValueError:
                p_fmt = 0.0
            try:
                q_fmt = int(txt_qtd.get())
            except ValueError:
                q_fmt = 0

            atualizar_produto(id_produto, txt_nome.get(), txt_dosagem.get(), p_fmt, q_fmt, txt_lab.get(),
                              txt_indicacao.get("1.0", "end-1c").strip())

            lbl_status.configure(text="✅ Alterações salvas com sucesso!", text_color="#2a994d")
            popup.after(1000, lambda: [popup.destroy(), self.carregar_tabela()])

        ctk.CTkButton(popup, text="Salvar Alterações", fg_color="#1f538d", command=salvar_alteracoes).pack(pady=25,
                                                                                                           padx=20,
                                                                                                           fill="x")
