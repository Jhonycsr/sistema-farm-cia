import  customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from funcoes.BancoDeDados import verificar_credenciais

class TelaLogin(ctk.CTkFrame):
    def __init__(self, master, ao_logar_sucesso, **kwargs):
        super().__init__(master, fg_color=("#F5F5F5", "#141414"), **kwargs)

        self.ao_logar_sucesso = ao_logar_sucesso

        self.card_login = ctk.CTkFrame(self, width=360, height=420, corner_radius=15, border_width=1, border_color="#2b2b2b")
        self.card_login.place(relx=0.5, rely=0.5, anchor="center")
        self.card_login.pack_propagate(False)

        # Titulo
        lbl_titulo = ctk.CTkLabel(self.card_login, text="🔒 Acessor ao Sistema", font=("Arial", 20, "bold"), text_color="#00adb5")
        lbl_titulo.pack(pady=(35, 30))

        # Campo: Usuario
        lbl_user = ctk.CTkLabel(self.card_login, text="Usuario", font=("Arial", 12, "bold"), text_color="#888")
        lbl_user.pack(anchor="w", padx=40, pady=(0, 2))

        self.ent_usuario = ctk.CTkEntry(self.card_login, width=280, height=35, placeholder_text="Digite seu usuário")
        self.ent_usuario.pack(padx=40, pady=(0, 15))

        # Campo: Senha
        lbl_pass = ctk.CTkLabel(self.card_login, text="Senha", font=("Arial", 12, "bold"), text_color="#888")
        lbl_pass.pack(anchor="w", padx=40, pady=(0, 2))

        self.ent_senha = ctk.CTkEntry(self.card_login, width=280, height=35, placeholder_text="Digite sua senha", show="*")
        self.ent_senha.pack(padx=40, pady=(0, 30))

        self.ent_senha.bind("<Return>", lambda event: self.tentar_login())
        self.ent_usuario.bind("<Return>", lambda event: self.tentar_login())

        # Botao Entrar
        self.btn_entrar = ctk.CTkButton(self.card_login, text="Entrar", width=280, height=40, font=("Arial", 14, "bold"), fg_color="#1f538d", command=self.tentar_login)
        self.btn_entrar.pack(padx=40)


    def tentar_login(self):
        usuario = self.ent_usuario.get().strip()
        senha = self.ent_senha.get().strip()

        if not usuario or not senha:
            CTkMessagebox(title="Campos Vazios", message="Por favor, preencha todos os campos!", icon="warning")
            return

        nivel_acesso = verificar_credenciais(usuario, senha)

        if nivel_acesso:
            self.ao_logar_sucesso(usuario, nivel_acesso)
        else:
            CTkMessagebox(title="Erro de Acesso", message="Usuario ou senha incorretos.", icon="cancel")

            self.ent_senha.delete(0, "end")
