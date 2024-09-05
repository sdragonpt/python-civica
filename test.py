from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('empresa.db')
cursor = conn.cursor()

# Função para redimensionar os widgets
def redimensionar(event):
    # Obter o novo tamanho da janela
    largura_nova = event.width
    altura_nova = event.height

    # Calcular fatores de escala com base no tamanho da janela inicial
    fator_escala_largura = largura_nova / largura_inicial
    fator_escala_altura = altura_nova / altura_inicial

    # Redimensionar os botões e textos com base no fator de escala
    tamanho_fonte_novo = int(tamanho_fonte_inicial * fator_escala_largura)

    botao_adicionar.config(font=("Arial", tamanho_fonte_novo))
    botao_truncar.config(font=("Arial", tamanho_fonte_novo))
    botao_exportar.config(font=("Arial", tamanho_fonte_novo))

    # Redimensionar a lista de inventário (labels dentro do frame)
    for widget in frame_lista.winfo_children():
        if isinstance(widget, Label):
            widget.config(font=("Arial", tamanho_fonte_novo))

    # Ajustar padding dos botões
    botao_adicionar.config(padx=int(20 * fator_escala_largura), pady=int(10 * fator_escala_altura))
    botao_truncar.config(padx=int(20 * fator_escala_largura), pady=int(10 * fator_escala_altura))
    botao_exportar.config(padx=int(20 * fator_escala_largura), pady=int(10 * fator_escala_altura))

# Função para exibir o inventário
def exibir_inventario():
    for widget in frame_lista.winfo_children():
        widget.destroy()

    cabecalho = ["ID", "Nº Artigo", "Nome", "Quantidade"]
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

# Função para abrir a janela de adição
def abrir_janela_adicao():
    janela_adicao = Toplevel(root)
    janela_adicao.title("Adicionar Item")
    janela_adicao.geometry("315x340")

    Label(janela_adicao, text="Número do Artigo").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_numero_artigo = Entry(janela_adicao)
    entry_numero_artigo.grid(row=0, column=1, padx=5, pady=5)

    Label(janela_adicao, text="Nome").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_nome = Entry(janela_adicao)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    Label(janela_adicao, text="Quantidade").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_quantidade = Entry(janela_adicao)
    entry_quantidade.grid(row=2, column=1, padx=5, pady=5)

    Button(janela_adicao, text="Salvar", command=lambda: adicionar_item(entry_numero_artigo, entry_nome, entry_quantidade, janela_adicao)).grid(row=5, column=0, padx=5, pady=5)
    Button(janela_adicao, text="Cancelar", command=janela_adicao.destroy).grid(row=5, column=1, padx=5, pady=5)

# Função para adicionar um item
def adicionar_item(entry_numero_artigo, entry_nome, entry_quantidade, janela_adicao):
    numero_artigo = entry_numero_artigo.get()
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()

    cursor.execute('''
        INSERT INTO inventario (numero_artigo, nome, quantidade)
        VALUES (?, ?, ?)
    ''', (numero_artigo, nome, quantidade))
    conn.commit()
    messagebox.showinfo("Sucesso", "Item adicionado com sucesso!")
    janela_adicao.destroy()
    exibir_inventario()

# Função para truncar a base de dados
def truncar_banco_de_dados():
    confirmacao = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir todos os dados do banco de dados?")
    if confirmacao:
        cursor.execute('DELETE FROM inventario')
        conn.commit()
        messagebox.showinfo("Sucesso", "Todos os dados foram excluídos!")
        exibir_inventario()

# Função para exportar os dados para Excel (placeholder)
def exportar_para_excel():
    messagebox.showinfo("Exportar", "Função de exportar para Excel ainda não implementada.")

# Tamanho da janela inicial
largura_inicial = 1280
altura_inicial = 1080

# Tamanho inicial dos textos
tamanho_fonte_inicial = 12

# Criação da interface gráfica
root = Tk()
root.geometry(f"{largura_inicial}x{altura_inicial}")
root.title("Gerenciador de Inventário")

# Frame para a tela inicial
frame_inicial = Frame(root)
frame_inicial.pack(fill=BOTH, expand=True)

# Botões na tela inicial
botao_adicionar = Button(frame_inicial, text="Adicionar Item", font=("Arial", tamanho_fonte_inicial), command=abrir_janela_adicao)
botao_adicionar.pack(pady=10)

botao_truncar = Button(frame_inicial, text="Truncar Base de Dados", font=("Arial", tamanho_fonte_inicial), command=truncar_banco_de_dados)
botao_truncar.pack(pady=10)

botao_exportar = Button(frame_inicial, text="Exportar para Excel", font=("Arial", tamanho_fonte_inicial), command=exportar_para_excel)
botao_exportar.pack(pady=10)

# Frame para a lista de inventário
frame_lista = Frame(frame_inicial)
frame_lista.pack(fill=BOTH, expand=True)

# Exibir inventário
exibir_inventario()

# Bind para redimensionamento
root.bind("<Configure>", redimensionar)

root.mainloop()
