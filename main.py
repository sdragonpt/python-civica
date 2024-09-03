import sqlite3
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Configuração do banco de dados
conn = sqlite3.connect('empresa.db')
cursor = conn.cursor()

# Criar a tabela inventario e fotos, caso não existam
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
item_id_para_atualizar = None

def adicionar_item():
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
    limpar_campos()
    exibir_inventario()
    janela_adicao.destroy()

def adicionar_foto():
    caminhos_fotos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")])
    for caminho in caminhos_fotos:
        lista_fotos.append(caminho)
        listbox_fotos.insert(END, caminho)

def limpar_campos():
    entry_numero_artigo.delete(0, END)
    entry_nome.delete(0, END)
    entry_quantidade.delete(0, END)
    listbox_fotos.delete(0, END)
    lista_fotos.clear()

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

        cursor.execute('SELECT caminho FROM fotos WHERE item_id = ?', (item_id,))
        fotos = cursor.fetchall()
        if fotos:
            for col, foto in enumerate(fotos):
                caminho = foto[0]
                img = Image.open(caminho)
                img.thumbnail((160, 160))  # Aumentar o tamanho da miniatura
                img_tk = ImageTk.PhotoImage(img)

                # Função para abrir a imagem em tamanho original
                def mostrar_imagem_original(caminho):
                    img_original = Image.open(caminho)
                    
                    # Definir o tamanho da janela (largura x altura)
                    largura_original, altura_original = img_original.size
                    largura_janela = min(largura_original, 800)  # Ajuste para a largura desejada
                    altura_janela = min(altura_original, 600)    # Ajuste para a altura desejada

                    janela_imagem = Toplevel(root)
                    janela_imagem.title("Imagem Original")
                    janela_imagem.geometry(f"{largura_janela}x{altura_janela}")  # Ajusta o tamanho da janela
                    
                    img_original.thumbnail((largura_janela, altura_janela))  # Redimensiona a imagem para se ajustar à janela
                    img_original_tk = ImageTk.PhotoImage(img_original)
                    label_imagem = Label(janela_imagem, image=img_original_tk)
                    label_imagem.image = img_original_tk
                    label_imagem.pack(fill=BOTH, expand=YES)

                label_foto = Label(frame_lista, image=img_tk, bg="#ffffff", borderwidth=1, relief="solid")
                label_foto.image = img_tk
                label_foto.grid(row=row_num + 1, column=4 + col, padx=5, pady=5)

                # Bind para clicar na foto e mostrar em tamanho original
                label_foto.bind("<Button-1>", lambda e, caminho=caminho: mostrar_imagem_original(caminho))


        botao_editar = Button(frame_lista, text="Editar", command=lambda item_id=item_id: carregar_item_para_edicao(item_id))
        botao_editar.grid(row=row_num + 1, column=5, padx=5, pady=5)
        
        botao_deletar = Button(frame_lista, text="Deletar", command=lambda item_id=item_id: deletar_item(item_id))
        botao_deletar.grid(row=row_num + 1, column=6, padx=5, pady=5)

    frame_lista.update()

def deletar_item(item_id):
    confirmacao = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o item ID {item_id}?")
    if confirmacao:
        cursor.execute('DELETE FROM inventario WHERE id = ?', (item_id,))
        cursor.execute('DELETE FROM fotos WHERE item_id = ?', (item_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Item ID {item_id} deletado com sucesso!")
        exibir_inventario()

def carregar_item_para_edicao(item_id):
    cursor.execute('SELECT * FROM inventario WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    
    if item:
        entry_numero_artigo.delete(0, END)
        entry_numero_artigo.insert(END, item[1])
        entry_nome.delete(0, END)
        entry_nome.insert(END, item[2])
        entry_quantidade.delete(0, END)
        entry_quantidade.insert(END, item[3])

        cursor.execute('SELECT caminho FROM fotos WHERE item_id = ?', (item_id,))
        fotos = cursor.fetchall()
        caminhos_fotos = [foto[0] for foto in fotos]

        global item_id_para_atualizar
        item_id_para_atualizar = item_id
        criar_janela_adicao(item[1], item[2], item[3], caminhos_fotos)

def atualizar_item():
    global item_id_para_atualizar
    if not item_id_para_atualizar:
        messagebox.showwarning("Atenção", "Nenhum item selecionado para atualizar.")
        return

    numero_artigo = entry_numero_artigo.get()
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()

    if not validar_quantidade(quantidade):
        messagebox.showerror("Erro", "Quantidade inválida. Deve ser um número inteiro positivo.")
        return

    cursor.execute('''
        UPDATE inventario 
        SET numero_artigo = ?, nome = ?, quantidade = ?
        WHERE id = ?
    ''', (numero_artigo, nome, quantidade, item_id_para_atualizar))

    cursor.execute('DELETE FROM fotos WHERE item_id = ?', (item_id_para_atualizar,))
    for foto in lista_fotos:
        cursor.execute('''
            INSERT INTO fotos (item_id, caminho)
            VALUES (?, ?)
        ''', (item_id_para_atualizar, foto))

    conn.commit()
    messagebox.showinfo("Sucesso", "Item atualizado com sucesso!")
    limpar_campos()
    exibir_inventario()
    janela_adicao.destroy()

def validar_quantidade(quantidade):
    try:
        valor = int(quantidade)
        return valor > 0
    except ValueError:
        return False

def adicionar_foto():
    caminhos_fotos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")])
    for caminho in caminhos_fotos:
        lista_fotos.append(caminho)
        listbox_fotos.insert(END, caminho)

def criar_janela_adicao(numero_artigo="", nome="", quantidade="", caminhos_fotos=[]):
    global janela_adicao, entry_numero_artigo, entry_nome, entry_quantidade, listbox_fotos, lista_fotos

    janela_adicao = Toplevel(root)
    janela_adicao.title("Adicionar/Editar Item")
    janela_adicao.geometry("500x400")

    Label(janela_adicao, text="Número do Artigo", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky=W)
    entry_numero_artigo = Entry(janela_adicao, font=("Arial", 12))
    entry_numero_artigo.grid(row=0, column=1, padx=10, pady=10)
    entry_numero_artigo.insert(END, numero_artigo)

    Label(janela_adicao, text="Nome", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky=W)
    entry_nome = Entry(janela_adicao, font=("Arial", 12))
    entry_nome.grid(row=1, column=1, padx=10, pady=10)
    entry_nome.insert(END, nome)

    Label(janela_adicao, text="Quantidade", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky=W)
    entry_quantidade = Entry(janela_adicao, font=("Arial", 12))
    entry_quantidade.grid(row=2, column=1, padx=10, pady=10)
    entry_quantidade.insert(END, quantidade)

    Label(janela_adicao, text="Fotos", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky=W)
    listbox_fotos = Listbox(janela_adicao, selectmode=SINGLE, font=("Arial", 12))
    listbox_fotos.grid(row=3, column=1, padx=10, pady=10)

    for caminho in caminhos_fotos:
        listbox_fotos.insert(END, caminho)
        lista_fotos.append(caminho)

    Button(janela_adicao, text="Adicionar Item", command=adicionar_item).grid(row=4, column=1, padx=10, pady=10)
    Button(janela_adicao, text="Adicionar Foto", command=adicionar_foto).grid(row=4, column=0, padx=10, pady=10)
    Button(janela_adicao, text="Atualizar", command=atualizar_item).grid(row=4, column=2, padx=10, pady=10)

def truncar_base_dados():
    confirmacao = messagebox.askyesno(
        "Confirmar Exclusão",
        "Você está prestes a truncar a base de dados. Isso removerá todos os itens e fotos. Deseja continuar?"
    )
    if confirmacao:
        try:
            cursor.execute('DELETE FROM fotos')
            cursor.execute('DELETE FROM inventario')
            conn.commit()
            messagebox.showinfo("Sucesso", "Base de dados truncada com sucesso!")
            exibir_inventario()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao truncar a base de dados: {e}")

# Configuração da janela principal
root = Tk()
root.title("Gerenciamento de Inventário")
root.geometry("900x500")

frame_lista = Frame(root)
frame_lista.pack(fill=BOTH, expand=True)

Button(root, text="Adicionar Item", command=lambda: criar_janela_adicao()).pack(side=LEFT, padx=10, pady=10)
Button(root, text="Truncar Base de Dados", command=truncar_base_dados).pack(side=LEFT, padx=10, pady=10)

exibir_inventario()
root.mainloop()
