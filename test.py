import sqlite3
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
import os

# Configuração do banco de dados
conn = sqlite3.connect('empresa.db')
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_artigo TEXT NOT NULL,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS fotos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        caminho TEXT,
        FOREIGN KEY (item_id) REFERENCES inventario(id) ON DELETE CASCADE
    )
''')

conn.commit()

# Variáveis globais e lista de fotos
lista_fotos = []

def limpar_campos_adicao(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos):
    entry_numero_artigo.delete(0, END)
    entry_nome.delete(0, END)
    entry_quantidade.delete(0, END)
    listbox_fotos.delete(0, END)
    lista_fotos.clear()  # Limpar a lista global de fotos

# Função para adicionar um novo item com fotos
def adicionar_item(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos, janela_adicao):
    numero_artigo = entry_numero_artigo.get()
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()
    
    cursor.execute('''
        INSERT INTO inventario (numero_artigo, nome, quantidade)
        VALUES (?, ?, ?)
    ''', (numero_artigo, nome, quantidade))
    item_id = cursor.lastrowid

    for foto in lista_fotos:
        cursor.execute('''
            INSERT INTO fotos (item_id, caminho)
            VALUES (?, ?)
        ''', (item_id, foto))

    conn.commit()
    messagebox.showinfo("Sucesso", "Item adicionado com sucesso!")

    # Limpar os campos para adicionar mais produtos
    limpar_campos_adicao(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos)

    #Atualiza o inventário
    exibir_inventario()

# Função para adicionar fotos
def adicionar_foto(entry_numero_artigo=None, entry_nome=None, entry_quantidade=None, listbox_fotos=None):
    caminhos_fotos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")])
    for caminho in caminhos_fotos:
        lista_fotos.append(caminho)
        if listbox_fotos is not None:
            listbox_fotos.insert(END, caminho)

# Função para limpar os campos da interface
def limpar_campos():
    global lista_fotos
    lista_fotos.clear()

# Função para exibir o inventário
def exibir_inventario():
    for widget in frame_lista.winfo_children():
        widget.destroy()

    cabecalho = ["ID", "Nº Artigo", "Nome", "Quantidade", "Fotos", "Editar", "Deletar"]
    for col, texto in enumerate(cabecalho):
        label = Label(frame_lista, text=texto, font=("Arial", 12, "bold"), bg="#f0f0f0", borderwidth=1, relief="solid")
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    cursor.execute('SELECT * FROM inventario')
    items = cursor.fetchall()

    for row_num, item in enumerate(items):
        item_id = item[0]
        numero_artigo = item[1]
        nome = item[2]
        quantidade = item[3]

        for col, valor in enumerate([item_id, numero_artigo, nome, quantidade]):
            label = Label(frame_lista, text=valor, font=("Arial", 10), bg="#ffffff", borderwidth=1, relief="solid")
            label.grid(row=row_num + 1, column=col, padx=5, pady=5, sticky="nsew")

        # Criar um frame para as fotos
        frame_fotos = Frame(frame_lista, bg="#ffffff")
        frame_fotos.grid(row=row_num + 1, column=4, padx=5, pady=5, sticky="nsew")
        
        cursor.execute('SELECT caminho FROM fotos WHERE item_id = ?', (item_id,))
        fotos = cursor.fetchall()
        for idx, foto in enumerate(fotos):
            caminho = foto[0]
            img = Image.open(caminho)
            img.thumbnail((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            label_foto = Label(frame_fotos, image=img_tk, bg="#ffffff", borderwidth=1, relief="solid")
            label_foto.image = img_tk
            label_foto.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)
            # Bind para clicar na foto e mostrar em tamanho original
            label_foto.bind("<Button-1>", lambda e, caminho=caminho: mostrar_imagem_original(caminho))

        botao_editar = Button(frame_lista, text="Editar", command=lambda item_id=item_id: abrir_janela_edicao(item_id))
        botao_editar.grid(row=row_num + 1, column=5, padx=5, pady=5)
        
        botao_deletar = Button(frame_lista, text="Deletar", command=lambda item_id=item_id: deletar_item(item_id))
        botao_deletar.grid(row=row_num + 1, column=6, padx=5, pady=5)

    frame_lista.update()

# Função para deletar um item do inventário
def deletar_item(item_id):
    confirmacao = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o item ID {item_id}?")
    if confirmacao:
        cursor.execute('DELETE FROM inventario WHERE id = ?', (item_id,))
        cursor.execute('DELETE FROM fotos WHERE item_id = ?', (item_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Item ID {item_id} deletado com sucesso!")
        exibir_inventario()

# Função para abrir a janela de edição
def abrir_janela_edicao(item_id):
    janela_edicao = Toplevel(root)
    janela_edicao.title("Editar Item")
    janela_edicao.geometry("315x340")

    # Garantir que a janela de adição fique sempre no topo
    janela_edicao.attributes('-topmost', True)
    
    Label(janela_edicao, text="Número do Artigo").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_numero_artigo = Entry(janela_edicao)
    entry_numero_artigo.grid(row=0, column=1, padx=5, pady=5)

    Label(janela_edicao, text="Nome").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_nome = Entry(janela_edicao)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    Label(janela_edicao, text="Quantidade").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_quantidade = Entry(janela_edicao)
    entry_quantidade.grid(row=2, column=1, padx=5, pady=5)

    Button(janela_edicao, text="Adicionar Foto", command=lambda: adicionar_foto(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos)).grid(row=3, column=0, columnspan=2, pady=5)

    listbox_fotos = Listbox(janela_edicao, width=50)
    listbox_fotos.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    cursor.execute('SELECT * FROM inventario WHERE id = ?', (item_id,))
    item = cursor.fetchone()

    if item:
        entry_numero_artigo.insert(END, item[1])
        entry_nome.insert(END, item[2])
        entry_quantidade.insert(END, item[3])
        
        cursor.execute('SELECT caminho FROM fotos WHERE item_id = ?', (item_id,))
        fotos = cursor.fetchall()
        global lista_fotos
        lista_fotos = [foto[0] for foto in fotos]

        for foto in lista_fotos:
            listbox_fotos.insert(END, foto)
    
    Button(janela_edicao, text="Salvar", command=lambda: atualizar_item(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos, janela_edicao, item_id)).grid(row=5, column=0, padx=5, pady=5)
    Button(janela_edicao, text="Cancelar", command=janela_edicao.destroy).grid(row=5, column=1, padx=5, pady=5)

# Função para atualizar um item do inventário
def atualizar_item(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos, janela_edicao, item_id):
    numero_artigo = entry_numero_artigo.get()
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()

    cursor.execute('''
        UPDATE inventario
        SET numero_artigo = ?, nome = ?, quantidade = ?
        WHERE id = ?
    ''', (numero_artigo, nome, quantidade, item_id))

    cursor.execute('DELETE FROM fotos WHERE item_id = ?', (item_id,))
    for foto in lista_fotos:
        cursor.execute('''
            INSERT INTO fotos (item_id, caminho)
            VALUES (?, ?)
        ''', (item_id, foto))

    conn.commit()
    messagebox.showinfo("Sucesso", f"Item ID {item_id} atualizado com sucesso!")
    janela_edicao.destroy()
    exibir_inventario()

# Função para truncar a base de dados
def truncar_banco_de_dados():
    confirmacao = messagebox.askyesno("Confirmar Truncamento", "Tem certeza que deseja excluir todos os dados do banco de dados?")
    if confirmacao:
        cursor.execute('DELETE FROM inventario')
        cursor.execute('DELETE FROM fotos')
        conn.commit()
        messagebox.showinfo("Sucesso", "Todos os dados foram excluídos!")
        exibir_inventario()

# Função para mostrar a imagem original
def mostrar_imagem_original(caminho):
    img_original = Image.open(caminho)
    janela_imagem = Toplevel(root)
    janela_imagem.title("Imagem Original")
    img_original_tk = ImageTk.PhotoImage(img_original)
    label_imagem = Label(janela_imagem, image=img_original_tk)
    label_imagem.image = img_original_tk
    label_imagem.pack()

# Função para exportar os dados para Excel
def exportar_para_excel():
    cursor.execute('''
        SELECT inventario.id, numero_artigo, nome, quantidade
        FROM inventario
    ''')
    dados = cursor.fetchall()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventário"

    colunas = ["ID", "Número do Artigo", "Nome", "Quantidade", "Fotos"]
    ws.append(colunas)

    for item in dados:
        item_id = item[0]
        numero_artigo = item[1]
        nome = item[2]
        quantidade = item[3]

        # Adicionar dados da linha
        ws.append([item_id, numero_artigo, nome, quantidade, ""])

        cursor.execute('SELECT caminho FROM fotos WHERE item_id = ?', (item_id,))
        fotos = cursor.fetchall()
        for idx, foto in enumerate(fotos):
            caminho = foto[0]
            img = OpenpyxlImage(caminho)
            img.width = 200  # Ajustar largura da imagem
            img.height = 200  # Ajustar altura da imagem
            cell = f'E{ws.max_row}'
            ws.add_image(img, cell)

    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Arquivos Excel", "*.xlsx")])
    if caminho_arquivo:
        wb.save(caminho_arquivo)
        messagebox.showinfo("Sucesso", "Dados exportados com sucesso!")

# Criação da interface gráfica
root = Tk()
root.title("Gerenciador de Inventário")

# Frame para a tela inicial
frame_inicial = Frame(root)
frame_inicial.pack(fill=BOTH, expand=True)

# Widgets para a tela inicial
botao_adicionar = Button(frame_inicial, text="Adicionar Item", command=lambda: abrir_janela_adicao())
botao_adicionar.pack(pady=10)

botao_truncar = Button(frame_inicial, text="Truncar Base de Dados", command=truncar_banco_de_dados)
botao_truncar.pack(pady=10)

botao_exportar = Button(frame_inicial, text="Exportar para Excel", command=exportar_para_excel)
botao_exportar.pack(pady=10)

frame_lista = Frame(frame_inicial)
frame_lista.pack(fill=BOTH, expand=True)
exibir_inventario()

def abrir_janela_adicao():
    janela_adicao = Toplevel(root)
    janela_adicao.title("Adicionar Item")
    janela_adicao.geometry("315x340")

    # Garantir que a janela de adição fique sempre no topo
    janela_adicao.attributes('-topmost', True)
    
    Label(janela_adicao, text="Número do Artigo").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_numero_artigo = Entry(janela_adicao)
    entry_numero_artigo.grid(row=0, column=1, padx=5, pady=5)

    Label(janela_adicao, text="Nome").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_nome = Entry(janela_adicao)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    Label(janela_adicao, text="Quantidade").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_quantidade = Entry(janela_adicao)
    entry_quantidade.grid(row=2, column=1, padx=5, pady=5)

    Button(janela_adicao, text="Adicionar Foto", command=lambda: adicionar_foto(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos)).grid(row=3, column=0, columnspan=2, pady=5)

    listbox_fotos = Listbox(janela_adicao, width=50)
    listbox_fotos.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    Button(janela_adicao, text="Salvar", command=lambda: adicionar_item(entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos, janela_adicao)).grid(row=5, column=0, padx=5, pady=5)
    Button(janela_adicao, text="Cancelar", command=janela_adicao.destroy).grid(row=5, column=1, padx=5, pady=5)

root.mainloop()
