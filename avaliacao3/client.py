import Pyro5.api
import Pyro5.client
# from Crypto.Signature import pkcs1_15
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA
import tkinter as tk
from tkinter import font as tkfont
import threading 

class Client(object):
    def __init__(self, manager_uri):

        self.name = "name"
        self.pub_key = "pubkey"
        self.manager = Pyro5.api.Proxy(manager_uri)
        self.daemon = Pyro5.api.Daemon()      # make a Pyro daemon
        self.uri = self.daemon.register(self)    # register the client as a Pyro object
        self.client_thread = threading.Thread(target=self.daemon.requestLoop)
        self.client_thread.start()
        #self.manager.register(self.name, self.pub_key, self.uri)
    
    @Pyro5.api.expose
    @Pyro5.api.callback
    def min_stock(self, item):
        print('item', item, 'is missing')

    @Pyro5.api.expose
    @Pyro5.api.callback
    def not_sold_report(self, items):
        print(items)

    def insert(self, code, name, description, qnt, price, minStorage):

        print(self.manager.insertItem(code, name, description, qnt, price, minStorage))

    def removeItem(self):
        nameServer = Pyro5.core.locate_ns()
        management_uri = nameServer.lookup("Management")
        managementServer = Pyro5.api.Proxy(management_uri)
        managementServer.removeItem()
        pass


client = Client("PYRONAME:management")

class UIMainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Ações Disponíveis", font=controller.title_font)
        label.grid()
        insertButton = tk.Button(self, text="Entrada de Produto",
                            command=lambda: controller.show_frame("InsertPage"))
        removeButton = tk.Button(self, text="Saída de Produto",
                            command=lambda: controller.show_frame("RemovePage"))
        reportButton = tk.Button(self, text="Geração de Relatório",
                            command=lambda: controller.show_frame("ReportPage"))
        insertButton.grid(row=1, column=0)
        removeButton.grid(row=2, column=0)
        reportButton.grid(row=3, column=0)
        self.grid_columnconfigure(0, weight=1)

class InsertPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Página de Entrada de Item", font=controller.title_font)
        label.grid(row = 0, column=1)
        tk.Label(self, text="Código").grid(row=1, column=0)
        tk.Label(self, text="Nome").grid(row=2, column=0)
        tk.Label(self, text="Descrição").grid(row=3, column=0)
        tk.Label(self, text="Quantidade").grid(row=4, column=0)
        tk.Label(self, text="Preço unitário").grid(row=5, column=0)
        tk.Label(self, text="Estoque mínimo").grid(row=6, column=0)
        codeEntry = tk.Entry(self)
        nameEntry = tk.Entry(self)
        descriptionEntry = tk.Entry(self)
        quantityEntry = tk.Entry(self)
        priceEntry = tk.Entry(self)
        minStorageEntry = tk.Entry(self)
        codeEntry.grid(row=1, column=1)
        nameEntry.grid(row=2, column=1)
        descriptionEntry.grid(row=3, column=1)
        quantityEntry.grid(row=4, column=1)
        priceEntry.grid(row=5, column=1)
        minStorageEntry.grid(row=6, column=1)
        button = tk.Button(self, text="Insere Item",
                           command= lambda: client.insert(codeEntry.get(), nameEntry.get(), descriptionEntry.get(), quantityEntry.get(),  priceEntry.get(), minStorageEntry.get()))
        button.grid(row=7, column=1)
        button = tk.Button(self, text="Returna à Página Principal",
                           command=lambda: controller.show_frame("UIMainPage"))
        button.grid(row=8, column=1)

class RemovePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Página de Saída de Item", font=controller.title_font)
        label.grid(row = 0, column=1)
        tk.Label(self, text="Código").grid(row=1, column=0)
        codeEntry = tk.Entry(self)
        codeEntry.grid(row=1, column=1)
        tk.Label(self, text="Quantidade").grid(row=2, column=0)
        quantityEntry = tk.Entry(self)
        quantityEntry.grid(row=2, column=1)
        button = tk.Button(self, text="Remove Item",
                           command=client.removeItem)
        button.grid(row=3, column=1)
        button = tk.Button(self, text="Returna à Página Principal",
                           command=lambda: controller.show_frame("UIMainPage"))
        button.grid(row=4, column=1)
    
class ReportPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Página de Geração de Relatório", font=controller.title_font)
        label.grid(row = 0, column=1)
        button = tk.Button(self, text="Returna à Página Principal",
                           command=lambda: controller.show_frame("UIMainPage"))
        button.grid(row=3, column=1)

class graphics(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (UIMainPage, InsertPage, RemovePage, ReportPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("UIMainPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


# def create_pair_key():
#     private_key = RSA.generate(2048)
#     public_key = private_key.publickey()

#     private_pem = private_key.export_key().decode()
#     public_pem = public_key.export_key().decode()
#     with open('private_pem.pem', 'w') as pr:
#         pr.write(private_pem)
#     with open('public_pem.pem', 'w') as pu:
#         pu.write(public_pem)



UI = graphics()
UI.mainloop()
