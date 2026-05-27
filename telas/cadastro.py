from PIL import Image, ImageDraw
import customtkinter as ctk
from funcoes.BancoDeDados import produto_ja_existe
import os
from CTkMessagebox import CTkMessagebox
from funcoes.BancoDeDados import salvar_produto, conectar_banco


class TelaCadastro(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.desenhar_elementos()

    def criar_quarto_circulo(self, caminho_imagem, tamanho):
        try:
            img = Image.open(caminho_imagem).convert("RGBA")
            img = img.resize((tamanho, tamanho))
            mascara = Image.new("L", (tamanho, tamanho), 0)
            draw = ImageDraw.Draw(mascara)
            draw.pieslice([(0, -tamanho), (tamanho * 2, tamanho)], start=90, end=180, fill=255)
            img.putalpha(mascara)
            return img
        except FileNotFoundError:
            return Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))


    def desenhar_elementos(self):
        # LOGO
        tamanho_logo = 200

        diretorio_telas = os.path.dirname(os.path.abspath(__file__))

        caminho_real_imagem = os.path.join(diretorio_telas, "..", "imagem.jpg")

        imagem_cortada = self.criar_quarto_circulo(caminho_imagem=caminho_real_imagem, tamanho=tamanho_logo)

        self.foto_logo = ctk.CTkImage(
            light_image=imagem_cortada,
            dark_image=imagem_cortada,
            size=(tamanho_logo, tamanho_logo)
        )

        label_logo = ctk.CTkLabel(self, image=self.foto_logo, text="")
        label_logo.grid(row=0, column=1, rowspan=4, sticky="ne", padx=(0, 0))

        # NOME
        label_nome = ctk.CTkLabel(self, text="Nome", font=("Arial", 16))
        label_nome.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.entry_nome = ctk.CTkEntry(self, width=300, placeholder_text="Ex: Paracetamol")
        self.entry_nome.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        self.entry_nome.focus()

        # DOSAGEM
        label_dosagem = ctk.CTkLabel(self, text="Dosagem", font=("Arial", 16))
        label_dosagem.grid(row=0, column=1, padx=(10, 100), pady=5, sticky="w")

        self.entry_dosagem = ctk.CTkEntry(self, width=150, placeholder_text="Ex: 500mg")
        self.entry_dosagem.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # PREÇO
        label_preco = ctk.CTkLabel(self, text="Preço", font=("Arial", 16))
        label_preco.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        frame_preco = ctk.CTkFrame(self, fg_color="transparent")
        frame_preco.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        label_cifrao = ctk.CTkLabel(frame_preco, text="R$", font=("Arial", 14, "bold"))
        label_cifrao.grid(row=0, column=0, padx=(0,5), sticky="w")

        self.entry_preco = ctk.CTkEntry(frame_preco, width=120, placeholder_text="0,00")
        self.entry_preco.grid(row=0, column=1, sticky="w")

        # QUANTIDADE
        label_quantidade = ctk.CTkLabel(self, text="Quantidade", font=("Arial", 16))
        label_quantidade.grid(row=2, column=1, padx=(10, 100), pady=5, sticky="w")

        self.entry_quantidade = ctk.CTkEntry(self, width=150, placeholder_text="Ex: 30")
        self.entry_quantidade.grid(row=3, column=1, padx=(10, 100), pady=5, sticky="w")

        # LABORATORIO
        label_laboratorio = ctk.CTkLabel(self, text="Laboratorio", font=("Arial", 16))
        label_laboratorio.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        self.entry_laboratorio = ctk.CTkEntry(self, width=150, placeholder_text="Neo Quimica")
        self.entry_laboratorio.grid(row=5, column=0, padx=20, pady=5, sticky="w")

        # INDICAÇAO
        label_indicacao = ctk.CTkLabel(self, text="Indicaçao", font=("Arial", 16))
        label_indicacao.grid(row=6, column=0, padx=20, pady=5, sticky="w")

        self.entry_indicacao = ctk.CTkTextbox(self, height=80)
        self.entry_indicacao.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        # BOTAO SALVAR
        self.lbl_mensagem = ctk.CTkLabel(self, text="", font=("Arial", 14, "bold"))
        self.lbl_mensagem.grid(row=8, column=0, columnspan=2, pady=(10, 0))

        btn_salvar = ctk.CTkButton(self, text="Cadastrar Produto", font=("Arial", 14, "bold"), fg_color="#1f538d", hover_color="#163b65", height=40, command=self.acao_botao_salvar)
        btn_salvar.grid(row=9, column=0, columnspan=2, padx=20, pady=25, sticky="ew")


        self.entry_nome.bind("<Return>", lambda e: self.acao_botao_salvar())
        self.entry_dosagem.bind("<Return>", lambda e: self.acao_botao_salvar())
        self.entry_preco.bind("<Return>", lambda e: self.acao_botao_salvar())
        self.entry_quantidade.bind("<Return>", lambda e: self.acao_botao_salvar())
        self.entry_laboratorio.bind("<Return>", lambda e: self.acao_botao_salvar())
        self.entry_indicacao.bind("<Return>", lambda e: self.acao_botao_salvar())



    def acao_botao_salvar(self):
        nome_tela = self.entry_nome.get().strip()
        dosagem_tela = self.entry_dosagem.get().strip()
        laboratorio_tela = self.entry_laboratorio.get().strip()
        indicacao_tela = self.entry_indicacao.get("1.0", "end-1c").strip()

        if not nome_tela or not dosagem_tela:
            CTkMessagebox(
                title="Campos Obrigatorios",
                message="⚠️ Nome e Dosagem sao obrigatorios para o cadastro!",
                icon="warning",
                option_1="Entendido"
            )
            return

        if produto_ja_existe(nome_tela, dosagem_tela):
            CTkMessagebox(
                title="Produto Ja Cadastrado",
                message=f"❌ O produto '{nome_tela} {dosagem_tela}' ja existe no sistema!",
                icon="warning",
                option_1="Voltar"
            )
            return

        try:
            preco_tela = float(self.entry_preco.get().replace(",","."))
        except ValueError:
            preco_tela = 0.0

        try:
            quantidade_tela = int(self.entry_quantidade.get())
        except ValueError:
            quantidade_tela = 0

        sucesso = salvar_produto(nome_tela, dosagem_tela, preco_tela, quantidade_tela, laboratorio_tela)

        if sucesso:
            CTkMessagebox(
                title="Sucesso",
                message=f"✅ O produto '{nome_tela}' foi cadastrado com sucesso!",
                icon="check",
                option_1="OK"
            )

            self.entry_nome.delete(0, "end")
            self.entry_dosagem.delete(0, "end")
            self.entry_preco.delete(0, "end")
            self.entry_quantidade.delete(0, "end")
            self.entry_laboratorio.delete(0, "end")
            self.entry_indicacao.delete("1.0", "end")
            self.entry_nome.focus()

        else:
            CTkMessagebox(
                title="Erro no Banco",
                message="❌ Erro interno ao tentar salvar o produto no banco de dados.",
                icon="cancel",
                option_1="OK"
            )

