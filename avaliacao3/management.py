import threading
import socket
import Pyro5.api
import Pyro5.socketutil
import time
from datetime import datetime, timedelta
# from Crypto.Signature import pkcs1_15
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA

# class NameServer(object):
#     def __init__(self):
#         self.hostname = socket.gethostname()
#         self.ip = Pyro5.socketutil.get_ip_address(None, workaround127=True)
#         # start a name server with broadcast server
#         self.nameserverUri, self.nameserverDaemon, self.broadcastServer = Pyro5.nameserver.start_ns(host=self.ip)
#         assert self.broadcastServer is not None, "expect a broadcast server to be created"
#         print("got a Nameserver, uri=%s" % self.nameserverUri)
#     def initDaemon(self): 
#         # create a Pyro daemon
#         pyrodaemon = Pyro5.api.Daemon(host=self.hostname)
#         serveruri = pyrodaemon.register(Management)
#         print("server uri=%s" % serveruri)
#         # register it with the nameserver
#         self.nameserverDaemon.nameserver.register("Management", serveruri)
#         self.nameserverDaemon.requestLoop()

class User():
    def __init__(self, name, pub_key, remote_obj):
        self.name = name
        self.pub_key = pub_key
        self.remote_obj = remote_obj
        
class Management(object):
    def __init__(self):
        self.estoque = {}
        self.users = []

        self.report_thread = threading.Thread(target=self.sendReport)
        self.report_thread.daemon = True
        self.report_thread.start()
    @Pyro5.api.expose
    def register(self, name, pub_key, uri):
        user_proxy = Pyro5.api.Proxy(uri)
        ### if user name pub ! exists
        for user in self.users:
            if(User.name != user.name and User.pub_key != user.pub_key and User.user_proxy != user.user_proxy):
                self.users.append(User(name,pub_key,user_proxy))
                return "Registration Completed"
        
        return "User already registered"
    
    #TODO: implementar
    def checkKey(self):
        return True

    #TODO: DATA E HORA
    @Pyro5.api.expose
    def insertItem(self, code, name, description, qnt, price, minStorage):
        if not self.checkKey():
            return "ERROR: Credenciais inválidas"

        current_time = datetime.now()

        print(self.estoque)
        if code in self.estoque:
            print('1')
            self.estoque[code]["name"] = name
            self.estoque[code]["description"] = description
            self.estoque[code]["price"] = price
            self.estoque[code]["minStorage"] = minStorage
            self.estoque[code]["qnt"] += qnt
            self.estoque[code]["last_insert_time"] = current_time

            return "Objeto inserido com sucesso"
        else:
            print('2')
            self.estoque[code] = {
                        "name": name,
                        "description": description,
                        "price": price,
                        "minStorage": minStorage,
                        "qnt": qnt,
                        "last_insert_time": current_time,
                        "last_remove_time": 0
                    }


            return "Novo objeto adicionado com sucesso"


    #TODO: DATA E HORA
    @Pyro5.api.expose
    def removeItem(self, code, qnt):
        if not self.checkKey():
            return "ERROR"
        
        current_time = datetime.now()

        if code in self.estoque:
            #if amount to remove is bigger than existing
            if qnt > self.estoque[code]["qnt"]:
                print('O estoque é insuficiente para ser retirada a quantidade pedida')
                return "ERROR: O estoque é insuficiente para ser retirada a quantidade pedida"
            if self.estoque[code]["qnt"]-qnt < self.estoque[code]["minStorage"]:
                #TODO: eniar flag estoque min p client
                for user in self.users:
                    user.remote_obj.min_stock(self.estoque[code]["name"])
                #return "1: "
            self.estoque[code]["qnt"] -= qnt
            self.estoque[code]["last_remove_time"] = current_time
            return "0: Operação concluída"
        else:
            print('O item requerido não está disponível')
            return 'ERROR: O item requerido não está disponível'
    
    @Pyro5.api.expose
    def getStock(self):
        return self.estoque
    #TODO: implementar propriamente
    def generateReport(self):
        notSold = []
        current_time = datetime.now()
        for code in self.estoque:
            if (current_time - self.estoque[code]["last_remove_time"]) > timedelta(minutes=2):
                notSold.append(code)
        return "report"
    def sendReport(self):
        while True:
            report = self.generateReport()
            for user in self.users:
                user.remote_obj.not_sold_report(report)
            time.sleep(60)  

if __name__ == "__main__":

    daemon = Pyro5.server.Daemon()         # make a Pyro daemon
    ns = Pyro5.api.locate_ns()             # find the name server
    uri = daemon.register(Management)   # register the greeting maker as a Pyro object
    ns.register("management", uri)   # register the object with a name in the name server
    daemon.requestLoop()   
#     managementServer = NameServer()
#     managementServer.initDaemon()

# print("Ready.")
