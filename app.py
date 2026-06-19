import customtkinter as ctk
import sqlite3
import os
import sqlite3
from PIL import Image  # IMPORTANTE: Adicione este import
import pytesseract


# Força o Python a encontrar o Tcl/Tk ignorando o espaço no nome do usuário
os.environ['TCL_LIBRARY'] = r"C:\Users\DANIEL~1\AppData\Local\Programs\Python\Python313-32\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\DANIEL~1\AppData\Local\Programs\Python\Python313-32\tcl\tk8.6"

# O restante do seu código continua igual abaixo:
app = ctk.CTk()


# Configuração inicial
ctk.set_appearance_mode('dark')

# Criando banco de dados
def criar_tabela():
    conexao = sqlite3.connect("resenhas.db")
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resenhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor TEXT NOT NULL,
            livro TEXT NOT NULL,
            resenha TEXT NOT NULL,
            arquivo TEXT
        )
    """)
    conexao.commit() #Inicia banco de dados da aplicação        
    conexao.close() #Sai do banco de dados

# Função para adicionar coluna 'arquivo' se não existir
def adicionar_coluna_arquivo():
    conexao = sqlite3.connect("resenhas.db")
    cursor = conexao.cursor()
    try:
        cursor.execute("ALTER TABLE resenhas ADD COLUMN arquivo TEXT")
        conexao.commit()
    except sqlite3.OperationalError:
        pass  # Caso a coluna já exista, não faz nada
    conexao.close()

# Função para alternar telas
def mostrar_tela(tela):
    tela_login.pack_forget()
    tela_principal.pack_forget()
    tela.pack(pady=10)

# Função de validação do login
def validar_login():
    usuario = campo_usu.get()
    senha = campo_senha.get()

    if usuario == 'Daniel' and senha == '12345':
        mostrar_tela(tela_principal)
        carregar_resenhas()
    else:
        resultado_login.configure(text='Login incorreto', text_color='red')

# Função para registrar resenha
def registrar_resenha():
    autor = campo_autor.get()
    livro = campo_livro.get()
    resenha = campo_resenha.get("1.0", "end-1c")  # Pegar o texto da caixa de resenha
    arquivo = campo_arquivo.get()  # Adicionando o campo de arquivo

    if autor and livro and resenha:
        conexao = sqlite3.connect("resenhas.db")
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO resenhas (autor, livro, resenha, arquivo) VALUES (?, ?, ?, ?)", (autor, livro, resenha, arquivo))
        conexao.commit()
        conexao.close()

        campo_autor.delete(0, "end")
        campo_livro.delete(0, "end")
        campo_resenha.delete("1.0", "end")
        campo_arquivo.delete(0, "end")  # Limpa o campo de arquivo

        carregar_resenhas()

# Função para carregar resenhas
def carregar_resenhas():
    for widget in frame_resenhas.winfo_children():
        widget.destroy()

    conexao = sqlite3.connect("resenhas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, autor, livro, resenha, arquivo FROM resenhas")  # Especificando as colunas
    resenhas = cursor.fetchall()
    conexao.close()

    for resenha in resenhas:
        id_resenha, autor, livro, texto_resenha, arquivo = resenha
        # Se o arquivo for None, definimos uma string vazia
        arquivo = arquivo if arquivo else ""
        
        frame_item = ctk.CTkFrame(frame_resenhas)
        frame_item.pack(pady=5, padx=5, fill="x")

        label_texto = ctk.CTkLabel(frame_item, text=f"{autor} - {livro}: {texto_resenha[:30]}...", anchor="w")
        label_texto.pack(side="left", padx=10)

        botao_editar = ctk.CTkButton(frame_item, text="✏️", width=30, command=lambda id=id_resenha: editar_resenha(id))
        botao_editar.pack(side="right", padx=5)

        botao_excluir = ctk.CTkButton(frame_item, text="🗑️", width=30, fg_color="red", command=lambda id=id_resenha: excluir_resenha(id))
        botao_excluir.pack(side="right", padx=5)

        if arquivo:
            botao_arquivo = ctk.CTkButton(frame_item, text="Abrir Arquivo", width=100, command=lambda arq=arquivo: abrir_arquivo(arq))
            botao_arquivo.pack(side="right", padx=5)

# Função para abrir arquivo (exemplo de como você pode implementá-la)
def abrir_arquivo(caminho_arquivo):
    print(f"Processando o arquivo: {caminho_arquivo}")
    
    # Verifica se o arquivo realmente existe
    if not os.path.exists(caminho_arquivo):
        print("Erro: Arquivo não encontrado.")
        return

    # Extensões de imagem comuns para aplicar o OCR
    extensoes_imagem = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    _, extensao = os.path.splitext(caminho_arquivo.lower())

    if extensao in extensoes_imagem:
        try:
            # 1. Abre a imagem usando a Pillow
            imagem = Image.open(caminho_arquivo)
            
            # 2. Executa o OCR para extrair o texto da imagem
            # O parâmetro 'lang' pode ser alterado (ex: 'por' para português, se tiver o pacote instalado)
            texto_extraido = pytesseract.image_to_string(imagem, lang='por')
            
            # Se não extrair nada, avisa o usuário
            if not texto_extraido.strip():
                texto_extraido = "[Não foi possível extrair nenhum texto legível desta imagem.]"

            # 3. Abre uma nova janela do CustomTkinter para exibir o texto do OCR
            janela_ocr = ctk.CTkToplevel(app)
            janela_ocr.title("Texto Extraído via OCR")
            janela_ocr.geometry("500x400")
            janela_ocr.lift()  # Garante que a janela fique na frente
            
            ctk.CTkLabel(janela_ocr, text="Texto detectado na foto da resenha:", font=("Arial", 14, "bold")).pack(pady=10)
            
            # Caixa de texto para o usuário ler e até copiar se quiser
            caixa_texto = ctk.CTkTextbox(janela_ocr, width=460, height=300)
            caixa_texto.insert("1.0", texto_extraido)
            caixa_texto.pack(pady=10, padx=10)
            
        except Exception as e:
            print(f"Erro ao processar o OCR da imagem: {e}")
            # Fallback: Se der erro no OCR, tenta abrir o arquivo normalmente no sistema
            os.startfile(caminho_arquivo) if hasattr(os, 'startfile') else os.system(f'open "{caminho_arquivo}"')
            
    else:
        # Se for um arquivo de texto, PDF ou outro formato, abre com o programa padrão do sistema
        try:
            if hasattr(os, 'startfile'):  # Windows
                os.startfile(caminho_arquivo)
            else:  # Mac / Linux
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, caminho_arquivo])
        except Exception as e:
            print(f"Erro ao abrir o arquivo: {e}")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# Função de Excluir resenhas 
def excluir_resenha(id_resenha):
    conexao = sqlite3.connect("resenhas.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM resenhas WHERE id = ?", (id_resenha,))
    conexao.commit()
    conexao.close()
    
    print(f"Resenha com ID {id_resenha} excluída.")
    carregar_resenhas()  # Atualiza a lista de resenhas na tela

#Função para editar resenha
def editar_resenha(id_resenha):
    print(f"Editando resenha com ID: {id_resenha}")
    # Aqui você pode abrir uma nova janela para editar a resenha

# Agora chame carregar_resenhas() corretamente
def carregar_resenhas():
    for widget in frame_resenhas.winfo_children():
        widget.destroy()

    conexao = sqlite3.connect("resenhas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, autor, livro, resenha, arquivo FROM resenhas")
    resenhas = cursor.fetchall()
    conexao.close()

    for resenha in resenhas:
        id_resenha, autor, livro, texto_resenha, arquivo = resenha
        arquivo = arquivo if arquivo else ""

        frame_item = ctk.CTkFrame(frame_resenhas)
        frame_item.pack(pady=5, padx=5, fill="x")

        label_texto = ctk.CTkLabel(frame_item, text=f"{autor} - {livro}: {texto_resenha[:30]}...", anchor="w")
        label_texto.pack(side="left", padx=10)

        botao_editar = ctk.CTkButton(frame_item, text="✏️", width=30, command=lambda id=id_resenha: editar_resenha(id))
        botao_editar.pack(side="right", padx=5)

        botao_excluir = ctk.CTkButton(frame_item, text="🗑️", width=30, fg_color="red", command=lambda id=id_resenha: excluir_resenha(id))
        botao_excluir.pack(side="right", padx=5)

        if arquivo:
            botao_arquivo = ctk.CTkButton(frame_item, text="Abrir Arquivo", width=100, command=lambda arq=arquivo: abrir_arquivo(arq))
            botao_arquivo.pack(side="right", padx=5)


def editar_resenha(id_resenha):
    # Criando a janela de edição
    janela_edicao = ctk.CTkToplevel(app)
    janela_edicao.title("Editar Resenha")
    janela_edicao.geometry("400x400")

    # Conectando ao banco para obter os dados atuais
    conexao = sqlite3.connect("resenhas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT autor, livro, resenha, arquivo FROM resenhas WHERE id = ?", (id_resenha,))
    resenha_atual = cursor.fetchone()
    conexao.close()

    if not resenha_atual:
        return  # Se não encontrar a resenha, apenas sai

    autor_atual, livro_atual, resenha_texto, arquivo_atual = resenha_atual

    # Campos de edição
    ctk.CTkLabel(janela_edicao, text="Autor").pack()
    campo_autor_edicao = ctk.CTkEntry(janela_edicao)
    campo_autor_edicao.insert(0, autor_atual)
    campo_autor_edicao.pack()

    ctk.CTkLabel(janela_edicao, text="Livro").pack()
    campo_livro_edicao = ctk.CTkEntry(janela_edicao)
    campo_livro_edicao.insert(0, livro_atual)
    campo_livro_edicao.pack()

    ctk.CTkLabel(janela_edicao, text="Resenha").pack()
    campo_resenha_edicao = ctk.CTkTextbox(janela_edicao, height=100, width=300)
    campo_resenha_edicao.insert("1.0", resenha_texto)
    campo_resenha_edicao.pack()

    ctk.CTkLabel(janela_edicao, text="Arquivo").pack()
    campo_arquivo_edicao = ctk.CTkEntry(janela_edicao)
    campo_arquivo_edicao.insert(0, arquivo_atual if arquivo_atual else "")
    campo_arquivo_edicao.pack()

    # Função para salvar edição
    def salvar_edicao():
        novo_autor = campo_autor_edicao.get()
        novo_livro = campo_livro_edicao.get()
        nova_resenha = campo_resenha_edicao.get("1.0", "end-1c")
        novo_arquivo = campo_arquivo_edicao.get()

        if novo_autor and novo_livro and nova_resenha:
            conexao = sqlite3.connect("resenhas.db")
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE resenhas 
                SET autor = ?, livro = ?, resenha = ?, arquivo = ? 
                WHERE id = ?
            """, (novo_autor, novo_livro, nova_resenha, novo_arquivo, id_resenha))
            conexao.commit()
            conexao.close()

            carregar_resenhas()  # Atualiza a tela principal
            janela_edicao.destroy()  # Fecha a janela de edição

    # Botão para salvar alterações
    botao_salvar = ctk.CTkButton(janela_edicao, text="Salvar", command=salvar_edicao)
    botao_salvar.pack(pady=10)

# Criando janela
app = ctk.CTk()
app.title("Sistema de Resenhas")
app.geometry("500x500")

# Tela de login pro enqunto o usuário é somente um
tela_login = ctk.CTkFrame(app)
tela_login.pack(pady=10) #pady define o espaçamento entre itens

label_usu = ctk.CTkLabel(tela_login, text="Usuário") #Label é uma funcionalidade semenlhante ao conceito do HTML

label_usu.pack()

campo_usu = ctk.CTkEntry(tela_login, placeholder_text="Digite seu usuário:")
campo_usu.pack()

label_senha = ctk.CTkLabel(tela_login, text="Senha")
label_senha.pack()

campo_senha = ctk.CTkEntry(tela_login, placeholder_text="Digite sua senha:", show="*")
campo_senha.pack()

botao_login = ctk.CTkButton(tela_login, text="Login", command=validar_login)
botao_login.pack(pady=10)

resultado_login = ctk.CTkLabel(tela_login, text="")
resultado_login.pack()

# Tela principal
tela_principal = ctk.CTkFrame(app)

# Campo para adicionar resenha
#AUTOR
ctk.CTkLabel(tela_principal, text="Autor").pack()
campo_autor = ctk.CTkEntry(tela_principal, placeholder_text="Nome do Autor")
campo_autor.pack()

#LIVRO
ctk.CTkLabel(tela_principal, text="Livro").pack()
campo_livro = ctk.CTkEntry(tela_principal, placeholder_text="Nome do Livro")
campo_livro.pack()

#RESENHA
ctk.CTkLabel(tela_principal, text="Resenha").pack()
campo_resenha = ctk.CTkTextbox(tela_principal, height=100, width=300)
campo_resenha.pack()

#ARQUIVO
ctk.CTkLabel(tela_principal, text="Arquivo").pack()
campo_arquivo = ctk.CTkEntry(tela_principal, placeholder_text="Caminho do arquivo (opcional)")
campo_arquivo.pack()

#BOTÃO DE REGISTRAR
botao_resgitrar = ctk.CTkButton(tela_principal, text="Registrar", command=registrar_resenha)
botao_resgitrar.pack(pady=10)

# Lista de resenhas
frame_resenhas = ctk.CTkFrame(tela_principal)
frame_resenhas.pack(fill="both", expand=True, pady=10)

#BOTÃO DE LOGOOF
botao_logout = ctk.CTkButton(tela_principal, text="Sair", command=lambda: mostrar_tela(tela_login))
botao_logout.pack(pady=10)

# Exibe tela de login primeiro
mostrar_tela(tela_login)

# Criar banco de dados
criar_tabela()
adicionar_coluna_arquivo()  # Chama para adicionar a coluna 'arquivo'

# Executar app
app.mainloop()


