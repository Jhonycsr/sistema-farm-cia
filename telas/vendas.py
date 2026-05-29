import sqlite3
import customtkinter as ctk
from customtkinter import CTkLabel
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib as plt
from matplotlib.lines import lineStyles
from funcoes.BancoDeDados import conectar_banco, buscar_historico_movimentacoes, dados_dashboard_7_dias, contar_estoque_critico
import unicodedata

class TelaVendas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        label_titulo = ctk.CTkLabel(self, text="Dashboard & Fluxo de Caixa", font=("Arial", 24, "bold"))
        label_titulo.pack(pady=(0, 20), anchor="w")

        self.frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cards.pack(fill="x", pady=(0, 15))
        self.frame_cards.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.labels_valores = {}
        self.criar_cards_fixos()

        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.pack(fill="both", expand=True)
        self.frame_inferior.grid_columnconfigure(0, weight=3)
        self.frame_inferior.grid_columnconfigure(1, weight=3)
        self.frame_inferior.grid_rowconfigure(0, weight=1)

        self.frame_grafico = ctk.CTkFrame(self.frame_inferior, fg_color="#141414", corner_radius=12, border_width=1, border_color="#2b2b2b")
        self.frame_grafico.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.frame_feed_container = ctk.CTkFrame(self.frame_inferior, fg_color="#141414", corner_radius=12, border_width=1, border_color="#2b2b2b")
        self.frame_feed_container.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(self.frame_feed_container, text="🕒 Fluxo de Saidas e Entradas", font=("Arial", 14, "bold"), text_color="#00adb5").pack(pady=12, padx=15, anchor="w")

        self.frame_filtros = ctk.CTkFrame(self.frame_feed_container, fg_color="transparent")
        self.frame_filtros.pack(fill="x", padx=15, pady=(0, 10))

        self.ent_busca = ctk.CTkEntry(self.frame_filtros, placeholder_text="🔍 Buscar produto, tipo ou lab...", height=30)
        self.ent_busca.pack(fill="x", side="top", pady=(0, 5))

        self.ent_busca.bind("<KeyRelease>", lambda event: self.agendar_filtro())

        self.feed_scroll = ctk.CTkScrollableFrame(self.frame_feed_container, fg_color="transparent")
        self.feed_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.fig = Figure(figsize=(5, 3.8), dpi=100)
        self.fig.patch.set_facecolor('#141414')
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.historico_completo = []
        self.historico_anterior = None

        self.search_timer = None

        self.atualizar_dashboard()
        self.loop_atualizacao_automatica()


    def vincular_scroll_mouse(self, widget):
        widget.bind("<Button-4>", lambda event: self.feed_scroll._parent_canvas.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda event: self.feed_scroll._parent_canvas.yview_scroll(1, "units"))

        for child in widget.winfo_children():
            self.vincular_scroll_mouse(child)


    def criar_cards_fixos(self):
        cards_confg = [
            ("faturamento", "Faturamento Bruto"),
            ("vendas", "Vendas Efetuadas"),
            ("saldo", "Saldo em Caixa"),
            ("alerta", "Estoque Critico ( < 5 un")
        ]

        for idx, (chave, titulo) in enumerate(cards_confg):
            c = ctk.CTkFrame(self.frame_cards, fg_color="#1a1a1a", height=85, corner_radius=8)
            c.grid(row=0, column=idx, padx=5, sticky="ew")
            c.grid_propagate(False)

            ctk.CTkLabel(c, text=titulo, font=("Arial", 11, "bold"), text_color="#aaa").pack(pady=(12, 0))

            lbl_valor = ctk.CTkLabel(c, text="...", font=("Arial", 18, "bold"))
            lbl_valor.pack(pady=3)
            self.labels_valores[chave] = lbl_valor

    def obter_totais_gerais(self):
        conexao = conectar_banco()
        if conexao is None:
            return 0.0, 0, 0.0
        try:
            cursor = conexao.cursor()

            cursor.execute("SELECT SUM(valor_total), COUNT(id) FROM movimentacoes WHERE tipo = 'VENDA'")
            res_vendas = cursor.fetchone()
            faturamento = res_vendas[0] if res_vendas[0] else 0.0
            total_vendas = res_vendas[1] if res_vendas[1] else 0

            cursor.execute("SELECT SUM(valor_total) FROM movimentacoes WHERE tipo = 'REPOSICAO'")
            res_gastos = cursor.fetchone()
            gastos = res_gastos[0] if res_gastos[0] else 0.0

            saldo_caixa = faturamento - gastos
            return faturamento, total_vendas, saldo_caixa
        except sqlite3.Error as e:
            print(f"❌ Erro ao calcular totais do dashboard: {e}")
            return 0.0, 0, 0.0
        finally:
            conexao.close()

    def atualizar_dashboard(self):
        fat, qtd, lucro = self.obter_totais_gerais()
        itens_criticos = contar_estoque_critico(limite=5)

        self.labels_valores["faturamento"].configure(text=f"R$ {fat:,.2f}".replace(".", ","), text_color="#1f538d")
        self.labels_valores["vendas"].configure(text=str(qtd), text_color="#2aa198")
        self.labels_valores["saldo"].configure(
            text=f"R$ {lucro:,.2f}".replace(".", ","),
            text_color="#2a944d" if lucro >= 0 else "#942a2a"
        )

        if itens_criticos > 0:
            texto_alerta = f"⚠️ {itens_criticos} PRODUTOS"
            cor_alerta = "#942a2a"

        else:
            texto_alerta = "✅ Tudo OK"
            cor_alerta = "#666"

        self.labels_valores["alerta"].configure(text=texto_alerta, text_color=cor_alerta)

        self.historico_completo = buscar_historico_movimentacoes()

        if self.historico_anterior == self.historico_completo:
            return

        self.historico_anterior = self.historico_completo

        self.historico_anterior = self.historico_completo
        self.filtrar_movimentacoes()
        self.renderizar_grafico_moderno()

    def filtrar_movimentacoes(self):
        self.search_timer = None

        termo_busca = self.remover_acentos_e_cedliha(self.ent_busca.get())

        widgets_antigos = self.feed_scroll.winfo_children()

        if not self.historico_completo:
            for w in widgets_antigos: w.destroy()
            ctk.CTkLabel(self.feed_scroll, text="Nenhuma atividade registrada.", text_color="#555",
                         font=("Arial", 12)).pack(pady=20)
            return

        registros_exibidos = 0
        novos_widgets = []

        for item in self.historico_completo:
            tipo, quantidade, valor_total, data, nome, dosagem, lab, usuario = item

            texto_busca_alvo = f"{tipo} {nome} {dosagem} {lab} {data}".lower()
            texto_busca_alvo = self.remover_acentos_e_cedliha(texto_busca_alvo)

            if termo_busca and termo_busca not in texto_busca_alvo:
                continue

            registros_exibidos += 1

            item_frame = ctk.CTkFrame(self.feed_scroll, fg_color="#1a1a1a", corner_radius=6, border_width=1,
                                      border_color="#222")

            valor_formatado = f"{valor_total:,.2f}".replace(".", ",")

            if str(tipo).upper() == "VENDA":
                texto_acao = f"💊 {nome} ({dosagem})"
                texto_sub = f"Saída de estoque • Por: {usuario} • Lab: {lab} • {data}"
                texto_preco = f"+ R$ {valor_formatado}"
                cor_preco = "#2a944d"
            else:
                texto_acao = f"📦 Reposição: {nome}"
                texto_sub = f"Entrada de +{quantidade} un. • Fornecedor • {data}"
                texto_preco = f"- R$ {valor_formatado}"
                cor_preco = "#942a2a"

            lbl_valor = ctk.CTkLabel(item_frame, text=texto_preco, font=("Arial", 13, "bold"), text_color=cor_preco)
            lbl_valor.pack(side="right", padx=15, pady=15)

            frame_textos = ctk.CTkFrame(item_frame, fg_color="transparent")
            frame_textos.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            lbl_info = CTkLabel(
                frame_textos,
                text=texto_acao,
                font=("Arial", 12, "bold"),
                anchor="w",
                justify="left"
            )
            lbl_info.pack(side="top", fill="x", anchor="w", pady=(0, 2))

            lbl_sub = ctk.CTkLabel(
                frame_textos,
                text=texto_sub,
                font=("Arial", 11),
                text_color="#888",
                justify="left",
                anchor="w"
            )
            lbl_sub.pack(side="top", fill="x", anchor="w")

            frame_textos.bind(
                "<Configure>",
                lambda event, f=frame_textos, l1=lbl_info, l2=lbl_sub: [
                    l1.configure(wraplength=max(100, f.winfo_width() - 20)),
                    l2.configure(wraplength=max(100, f.winfo_width() - 20))
                ]
            )

            self.vincular_scroll_mouse(item_frame)
            novos_widgets.append(item_frame)

        for w in widgets_antigos:
            w.destroy()

        for w in novos_widgets:
            w.pack(fill="x", pady=4, padx=5)

        if registros_exibidos == 0:
            ctk.CTkLabel(self.feed_scroll, text="Nenhum resultado encontrado.", text_color="#555",
                         font=("Arial", 12)).pack(pady=20)

    def renderizar_grafico_moderno(self):
        dados_banco = dados_dashboard_7_dias()

        if dados_banco:
            dias = [row[0][-5:] for row in dados_banco if row[0]]
            valores = [float(row[1]) if row[1] is not None else 0.0 for row in dados_banco]
            vendas_qtd = [int(row[2]) if row[2] is not None else 0 for row in dados_banco]
        else:
            dias, valores, vendas_qtd = ["Sem dados"], [0.0], [0]

        if not (len(dias) == len(valores) == len(vendas_qtd)):
            tamanho_seguro = min(len(dias), len(valores), len(vendas_qtd))
            dias = dias[:tamanho_seguro]
            valores = valores[:tamanho_seguro]
            vendas_qtd = vendas_qtd[:tamanho_seguro]

        self.ax.clear()
        self.ax.set_facecolor('#141414')

        barras = self.ax.bar(dias, valores, color='#00adb5', width=0.4, alpha=0.85, edgecolor='#00f5ff', linewidth=0.5)

        if len(dias) == 1:
            self.ax.set_xlim(-1, 1)
        else:
            self.ax.set_xlim(None, None)

        self.ax.tick_params(colors='#888', labelsize=9)
        self.ax.spines['bottom'].set_color('#2b2b2b')
        self.ax.spines['left'].set_color('#2b2b2b')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(True, color='#222', linestyle=':', linewidth=0.7, axis='y')
        self.ax.set_title("Faturamento dos Ultimos Dias com Vendas", color='white', fontsize=11, pad=15, fontweight='bold')

        annot = self.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.5", fc="#222", ec="#00adb5", lw=1),
                            arrowprops=dict(arrowstyle="->", color="#00adb5"), color="white", fontsize=9)
        annot.set_visible(False)


        def update_annot(bar, idx):
            x = bar.get_x() + bar.get_width() / 2
            y = bar.get_height()
            annot.xy = (x, y)
            text= f"Dia: {dias[idx]}\nTotal: R$ {valores[idx]}\nCupons: {vendas_qtd[idx]}"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.9)


        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == self.ax:
                for idx, bar in enumerate(barras):
                    cont, _ = bar.contains(event)
                    if cont:
                        if idx < len(dias):
                            update_annot(bar, idx)
                            annot.set_visible(True)
                            bar.set_color('#00f5ff')
                            self.fig.canvas.draw_idle()
                        return

            if vis:
                annot.set_visible(False)
                for bar in barras:
                    bar.set_color('#00adb5')
                self.fig.canvas.draw_idle()

        if hasattr(self, '_hover_cid'):
            self.fig.canvas.mpl_disconnect(self._hover_cid)
        self._hover_cid = self.fig.canvas.mpl_connect("motion_notify_event", hover)

        self.canvas.draw_idle()

    def loop_atualizacao_automatica(self):
        self.after(2000, self.loop_atualizacao_automatica)
        self.atualizar_dashboard()


    def remover_acentos_e_cedliha(self, texto):
        if not texto:
            return ""

        texto = texto.lower().strip()
        texto = texto.replace("ç", "c")

        nfkd_form = unicodedata.normalize('NFKD', texto)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


    def agendar_filtro(self):
        if self.search_timer is not None:
            self.after_cancel(self.search_timer)

        self.search_timer = self.after(300, self.filtrar_movimentacoes)

