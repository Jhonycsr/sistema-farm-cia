import customtkinter as ctk
from funcoes.BancoDeDados import conectar_banco
from telas.cadastro import TelaCadastro
from telas.listagem import TelaListagem
from telas.vendas import TelaVendas

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SistemaFarmacia(ctk.CTk):
    def __init__(self):
        super().__init__()

        conectar_banco()

        self.geometry("1050x680")
        self.title("Sistema de Gestao - Farmacia")
        ctk.set_appearance_mode("dark")

        self.menu_expandido = True

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_lateral = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_lateral.grid(row=0, column=0, sticky="nsew")
        self.frame_lateral.grid_propagate(False)

        self.frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_conteudo.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.criar_menu_lateral()

        self.mostrar_tela_vendas()

    def criar_menu_lateral(self):

        self.btn_menu = ctk.CTkButton(self.frame_lateral, text="☰ Menu", fg_color="transparent", text_color="white", anchor="w", command=self.alterar_menu)
        self.btn_menu.pack(fill="x", padx=10, pady=(20, 30))

        self.btn_cadastro = ctk.CTkButton(self.frame_lateral, text="➕ Cadastrar Produto", fg_color="transparent", anchor="w", command=self.mostrar_tela_cadastro)
        self.btn_cadastro.pack(fill="x", padx=10, pady=5)

        self.btn_listagem = ctk.CTkButton(self.frame_lateral, text="📋 Lista de Estoque", fg_color="transparent", anchor="w", command=self.mostrar_tela_listagem)
        self.btn_listagem.pack(fill="x", padx=10, pady=5)

        self.btn_vendas = ctk.CTkButton(self.frame_lateral, text="💰 Vendas Diarias", fg_color="transparent", anchor="w", command=self.mostrar_tela_vendas)
        self.btn_vendas.pack(fill="x", padx=10, pady=5)

    def alterar_menu(self):
        botoes = [self.btn_menu, self.btn_cadastro, self.btn_listagem, self.btn_vendas]
        if self.menu_expandido:
            self.frame_lateral.configure(width=60)
            self.grid_columnconfigure(0, minsize=60, weight=0)
            for btn in botoes:
                btn.configure(width=40)
            self.btn_menu.configure(text="☰")
            self.btn_cadastro.configure(text="➕")
            self.btn_listagem.configure(text="📋")
            self.btn_vendas.configure(text="💰")

            self.menu_expandido = False

        else:
            self.frame_lateral.configure(width=200)
            self.grid_columnconfigure(0, minsize=200, weight=0)
            for btn in botoes:
                btn.configure(width=180)
            self.btn_menu.configure(text="☰ Menu")
            self.btn_cadastro.configure(text="➕ Cadastrar Produto")
            self.btn_listagem.configure(text="📋 Lista de Estoque")
            self.btn_vendas.configure(text="💰 Vendas Diárias")

            self.menu_expandido = True

        self.update()
        self.frame_lateral.update()

    def limpar_frame_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()


    def destacar_botao(self, botao_ativo):
        for btn in [self.btn_cadastro, self.btn_listagem, self.btn_vendas]:
            if btn == botao_ativo:
                btn.configure(fg_color="#1f538d")
            else:
                btn.configure(fg_color="transparent")

    def mostrar_tela_cadastro(self):
        self.limpar_frame_conteudo()
        self.destacar_botao(self.btn_cadastro)

        self.tela_atual = TelaCadastro(self.frame_conteudo)
        self.tela_atual.pack(fill="both", expand=True)

    def mostrar_tela_listagem(self):
        self.limpar_frame_conteudo()
        self.destacar_botao(self.btn_listagem)

        self.tela_atual = TelaListagem(self.frame_conteudo)
        self.tela_atual.pack(fill="both", expand=True)

    def mostrar_tela_vendas(self):
        self.limpar_frame_conteudo()
        self.destacar_botao(self.btn_vendas)

        self.tela_atual = TelaVendas(self.frame_conteudo)
        self.tela_atual.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = SistemaFarmacia()
    largura = app.winfo_screenmmwidth()
    altura = app.winfo_height()
    app.geometry(f"{largura}x{altura}+0+0")
    app.mainloop()
