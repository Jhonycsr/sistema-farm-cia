# 🏥 Sistema de Gestão de Farmácia

Um sistema de desktop moderno, rápido e intuitivo para o gerenciamento de estoque e controle de fluxo de caixa (entradas e saídas) voltado para farmácias. O projeto foi desenvolvido com foco em modularização de código, separando a interface gráfica da lógica de banco de dados.

## 🚀 Funcionalidades

* **Controle de Estoque:** Cadastro, edição, listagem e exclusão (CRUD) de medicamentos com informações de dosagem, preço, laboratório e indicação médica.
* **Fluxo de Saídas (Vendas):** Registro de vendas integrado com abatimento automático e validação de estoque atual para impedir saldos negativos.
* **Fluxo de Entradas (Reposição):** Registro rápido de entrada de novos lotes de medicamentos com atualização automática do inventário.
* **Interface Dinâmica:** Layout responsivo em modo escuro utilizando listas roláveis com suporte corrigido a rolagem pelo mouse no Linux.
* **Histórico Visual:** Tela dedicada para acompanhar o fluxo financeiro de entradas (com destaques em vermelho) e saídas (com destaques em verde).

## 🛠️ Tecnologias Utilizadas

* **Python 3.12** (Linguagem base do projeto)
* **CustomTkinter** (Interface gráfica moderna e costumizável baseada em Tkinter)
* **SQLite3** (Banco de dados relacional leve e local)

## 📁 Estrutura do Projeto

```text
├── funcoes/
│   ├── BancoDeDados.py      # Toda a lógica de conexões, queries e manipulação do SQLite3
│   └── __init__.py
├── telas/
│   ├── cadastro.py          # Interface e lógica da tela de inserção de medicamentos
│   ├── listagem.py          # Tabela dinâmica de exibição, edição e ações do estoque
│   └── vendas.py            # Tela com o histórico do fluxo de entradas e saídas
├── __main__.py              # Arquivo principal que gerencia a inicialização e troca de telas
└── farmacia.db              # Arquivo local do banco de dados

🔧 Como Executar o Projeto
Pré-requisitos:
Certifique-se de ter o Python 3.12 instalado na sua máquina.

Passo a Passo:
1-Clone este repositório ou baixe os arquivos em sua máquina.
2-Abra o terminal na pasta do projeto.
3-Instale as dependências necessárias utilizando o gerenciador de pacotes:
              pip install customtkinter
4-Execute o arquivo principal para iniciar a aplicação:
              python3 __main__.py
