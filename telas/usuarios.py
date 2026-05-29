import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from funcoes.BancoDeDados import listar_usuarios, cadastrar_novo_usuario, excluir_usuario

class TelaUsuarios(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        label_titulo = ctk.CTkLabel(self, text="👥 Gerenciamento de Funcionarios", font=("Arial", 24, "bold"))
        label_titulo.pack(pady=(0, 20), anchor="w")

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.pack(fill="both", expand=True)

        self.container_principal.grid_columnconfigure(0, weight=2)
        self.container_principal.grid_columnconfigure(1, weight=3)
        self.container_principal.grid_rowconfigure(0, weight=1)

        self.frame_form = ctk.CTkFrame(self.container_principal, fg_color="#141414", corner_radius=12, border_width=1, border_color="#2b2b2b")
        self.frame_form.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(self.frame_form, text="➕ Novo Funcinario", font=("Arial", 14, "bold"), text_color="#00adb5").pack(pady=15, padx=15, anchor="w")

        ctk.CTkLabel(self.frame_form, text="Nome de Usuario", font=("Arial", 11, "bold"), text_color="#888").pack(anchor="w", padx=20)
        self.ent_user = ctk.CTkEntry(self.frame_form, placeholder_text="ex: nome.atendente")
        self.ent_user.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.frame_form, text="Senha Inicial", font=("Arial", 11, "bold"), text_color="#888").pack(anchor="w", padx=20)
        self.ent_pass = ctk.CTkEntry(self.frame_form, placeholder_text="Digite a senha", show="*")
        self.ent_pass.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.frame_form, text="Nivel de Acesso", font=("Arial", 11, "bold"), text_color="#888").pack(anchor="w", padx=20)
        self.radio_var = ctk.StringVar(value="ATENDENTE")

        self.rb_atendente = ctk.CTkRadioButton(self.frame_form, text="Atendente", variable=self.radio_var, value="ATENDENTE")
        self.rb_atendente.pack(anchor="w", padx=30, pady=5)

        self.rb_admin = ctk.CTkRadioButton(self.frame_form, text="Adminstrador", variable=self.radio_var, value="ADMINISTRADOR")
        self.rb_admin.pack(anchor="w", padx=30, pady=(5, 30))

        self.btn_salvar = ctk.CTkButton(self.frame_form, text="Cadastrar", font=("Arial", 13, "bold"), fg_color="#1f538d", command=self.salvar_usuario)
        self.btn_salvar.pack(fill="x", padx=20, pady=10)

        self.frame_lista_container = ctk.CTkFrame(self.container_principal, fg_color="#141414", corner_radius=12, border_width=1, border_color="#2b2b2b")
        self.frame_lista_container.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(self.frame_lista_container, text="📋 Usuarios Cadastrados", font=("Arial", 14, "bold"), text_color="#00adb5").pack(pady=15, padx=15, anchor="w")

        self.scroll_usuarios = ctk.CTkScrollableFrame(self.frame_lista_container, fg_color="transparent")
        self.scroll_usuarios.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.atualizar_lista_usuarios()

        self.update_idletasks()


    def atualizar_lista_usuarios(self):
        for w in self.scroll_usuarios.winfo_children():
            w.destroy()

        usuarios = listar_usuarios()

        for id_user, nome, nivel in usuarios:
            item = ctk.CTkFrame(self.scroll_usuarios, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#222")
            item.pack(fill="x", pady=4, padx=5)

            cor_nivel = "#2aa198" if nivel == "ADMINISTRADOR" else "#aaa"
            lbl_info = ctk.CTkLabel(item, text=f"👤 {nome} • ", font=("Arial", 12, "bold"), anchor="w")
            lbl_info.pack(side="left", padx=(15, 0), pady=10)

            lbl_nivel = ctk.CTkLabel(item, text=nivel, font=("Arial", 10, "bold"), text_color=cor_nivel)
            lbl_nivel.pack(side="left", pady=10)

            if nome != "admin":
                btn_del = ctk.CTkButton(
                    item, text="❌", width=30, height=25, fg_color="transparent",
                    hover_color="#942a2a", text_color="#888",
                    command=lambda i=id_user, n=nome: self.deletar_usuario(i, n)
                )
                btn_del.pack(side="right", padx=15, pady=8)


    def salvar_usuario(self):
        user = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()
        nivel = self.radio_var.get()

        if not user or not senha:
            CTkMessagebox(title="Aviso", message="Preencha todos os campos!", icon="warning")
            return

        sucesso, msg = cadastrar_novo_usuario(user, senha, nivel)

        if sucesso:
            CTkMessagebox(title="Sucesso", message=msg, icon="check")
            self.ent_user.delete(0, "end")
            self.ent_pass.delete(0, "end")
            self.radio_var.set("ATENDENTE")
            self.atualizar_lista_usuarios()

            self.focus_set()
        else:
            CTkMessagebox(title="Erro", message=msg, icon="cancel")


    def deletar_usuario(self, id_user, nome_user):
        pergunta = CTkMessagebox(title="Confirmar", message=f"Tem certe que deseja remover o usuario '{nome_user}'?", icon="question", option_1="Nao", option_2="Sim")
        if pergunta.get() == "Sim":
            excluir_usuario(id_user)
            CTkMessagebox(title="Sucesso", message="Usuario removido!", icon="check")
            self.atualizar_lista_usuarios()
        else:
            CTkMessagebox(title="Erro", message="Nao foi possivel remover o usuario.", icon="cancel")
            return
