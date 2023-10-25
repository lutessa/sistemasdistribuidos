import threading
import socket
import Pyro5.api
import Pyro5.socketutil
import time
from datetime import datetime, timedelta
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

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
        
        self.estoque_lock = threading.Lock()  


        self.daemon = Pyro5.server.Daemon()
        self.uri = self.daemon.register(self)
        self.ns = Pyro5.api.locate_ns()
        self.ns.register("management", self.uri)


        self.report_thread = threading.Thread(target=self.sendReport)
        self.report_thread.daemon = True
        self.report_thread.start()


        self.daemon_thread = threading.Thread(target=self.run_daemon)
        self.daemon_thread.daemon = True
        self.daemon_thread.start()


    @Pyro5.api.expose
    def register(self, name, pub_key, uri):
        #user_proxy = Pyro5.api.Proxy(uri)
        ### if user name pub ! exists
        # for user in self.users:
        #     if(User.name == use.name and User.pub_key == user.pub_key and User.user_proxy == user.user_proxy):
        #         return "User already registered"

        self.users.append(User(name,pub_key,uri))
        
        return "Registration Completed"
        
    #TODO: implementar
    def checkKey(self, public_key, signature):
        # hash.update(signature)
        key = RSA.import_key(bytes(public_key))
        print("pub_key:",key)
        try:
            # verifier = pkcs1_15.new(RSA.import_key(bytes(public_key)))
            # hash = SHA256.new(b'signed')
            # verifier.verify(hash, bytes(signature))
            pkcs1_15.new(RSA.import_key(bytes(public_key))).verify(SHA256.new(b'signed'), bytes(signature))
            print('Signature is valid.')
            return 1
        except:
            print('Signature is invalid.')
            return 0

    #TODO: DATA E HORA
    @Pyro5.api.expose
    def insertItem(self, code, name, description, qnt, price, minStorage, uri, signature):
        actual_user = None
        for user in self.users:
            if user.remote_obj == uri:
                actual_user = user
                # print("server name:", actual_user.name)
                # print("server uri:", actual_user.remote_obj)
                # print("server pub_key:", actual_user.pub_key)
        if actual_user == None:
            print('Not a valid user')
            return -1
            
        # self.checkKey(actual_user.pub_key, signature)
            # return "ERROR: Credenciais inválidas"
        try:
            # verifier = pkcs1_15.new(RSA.import_key(bytes(public_key)))
            # hash = SHA256.new(b'signed')
            # verifier.verify(hash, bytes(signature))
            pkcs1_15.new(RSA.import_key(bytes(actual_user.pub_key))).verify(SHA256.new(b'signed'), bytes(signature))
            print('Signature is valid.')
        except:
            print('Signature is invalid.')
            return 0

        current_time = datetime.now()

        with self.estoque_lock:
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
                            "last_remove_time": datetime.fromtimestamp(0)
                        }
                return "Novo objeto adicionado com sucesso"

    #TODO: DATA E HORA
    @Pyro5.api.expose
    def removeItem(self, code, qnt, uri, signature):
        actual_user = None
        for user in self.users:
            if user.remote_obj == uri:
                actual_user = user                
        try:
            # verifier = pkcs1_15.new(RSA.import_key(bytes(public_key)))
            # hash = SHA256.new(b'signed')
            # verifier.verify(hash, bytes(signature))
            pkcs1_15.new(RSA.import_key(bytes(actual_user.pub_key))).verify(SHA256.new(b'signed'), bytes(signature))
            print('Signature is valid.')
        except:
            print('Signature is invalid.')
            return 0
        
        current_time = datetime.now()
        with self.estoque_lock:
            if code in self.estoque:
                #if amount to remove is bigger than existing
                if qnt > self.estoque[code]["qnt"]:
                    print('O estoque é insuficiente para ser retirada a quantidade pedida')
                    return "ERROR: O estoque é insuficiente para ser retirada a quantidade pedida"
                if self.estoque[code]["qnt"]-qnt < self.estoque[code]["minStorage"]:
                    #TODO: eniar flag estoque min p client
                    print("sending flag")
                    
                    for user in self.users:
                        print("sending flag")
                        user_proxy = Pyro5.api.Proxy(user.remote_obj) 
                        user_proxy.min_stock(self.estoque[code]["name"])
                    #return "1: "
                    
                self.estoque[code]["qnt"] -= qnt
                self.estoque[code]["last_remove_time"] = current_time
                return "0: Operação concluída"
            else:
                print('O item requerido não está disponível')
                return 'ERROR: O item requerido não está disponível'
    
    @Pyro5.api.expose
    def getStock(self):
        with self.estoque_lock:
            return self.estoque
        
    @Pyro5.api.expose
    def notSoldTime(self, datetime_limit):
        items = []
        print('datetime_limit:',datetime_limit)
        with self.estoque_lock:
            datetime_limit = datetime.strptime(datetime_limit,'%Y-%m-%dT%H:%M:%S')
            for code in self.estoque:
                last_remove_time = self.estoque[code]["last_remove_time"]
                print('last_remove_time:',last_remove_time)
                # last_remove_time = datetime.strptime(self.estoque[code]["last_remove_time"],'%Y-%m-%dT%H:%M:%S')
                if (last_remove_time == 0) or (last_remove_time < datetime_limit):
                    items.append(self.estoque[code])
        return items
    
    @Pyro5.api.expose
    def get_flow(self, start_datetime, end_datetime):
        items = [] 
        if isinstance(start_datetime, str):
            start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
        
        if isinstance(end_datetime, str):
        
            end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')
        
        with self.estoque_lock:
            for code in self.estoque:
                last_insert_time = self.estoque[code]["last_insert_time"]
                if isinstance(last_insert_time, str):
                    last_insert_time = datetime.strptime(self.estoque[code]["last_insert_time"], '%Y-%m-%dT%H:%M:%S')
                last_remove_time = self.estoque[code]["last_remove_time"]
                if isinstance(last_remove_time, str):
                    last_remove_time = datetime.strptime(self.estoque[code]["last_remove_time"], '%Y-%m-%dT%H:%M:%S')

                if (((last_remove_time > start_datetime) and (last_remove_time < end_datetime)) or ((last_insert_time > start_datetime) and (last_insert_time < end_datetime))):
                    items.append(self.estoque[code])
        return items

    #TODO: implementar propriamente
    def generateReport(self):
        with self.estoque_lock:
            notSold = []
            current_time = datetime.now()
            time_limite = current_time - timedelta(minutes=2)

            for code in self.estoque:

                last_remove_time = self.estoque[code]["last_remove_time"]
                if last_remove_time != 0:

                    if isinstance(last_remove_time, str):
                        last_remove_time = datetime.strptime(last_remove_time, '%Y-%m-%d %H:%M:%S.%f')
                    if isinstance(last_remove_time, datetime):
                        last_remove_timestamp = int(last_remove_time.timestamp())
                        if last_remove_timestamp < int(time_limite.timestamp()):
                            notSold.append(code)
                else:
                    last_insert_time = self.estoque[code]["last_insert_time"]
                    if isinstance(last_insert_time, str):
                        last_insert_time = datetime.strptime(last_insert_time, '%Y-%m-%d %H:%M:%S.%f')
                    if isinstance(last_insert_time, datetime):
                        last_insert_timestamp = int(last_insert_time.timestamp())
                        if last_insert_timestamp < int(time_limite.timestamp()):
                            notSold.append(code)
            print(notSold)
            return notSold

    def sendReport(self):
        while True:
            print("sending reports")
            report = self.generateReport()
            for user in self.users:
                user_proxy = Pyro5.api.Proxy(user.remote_obj) 
                user_proxy.not_sold_report(report)
            time.sleep(60)  

    def run_daemon(self):
        self.daemon.requestLoop()

if __name__ == "__main__":

    manager = Management()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando o programa...")
        manager.daemon.shutdown()
        manager.daemon_thread.join()
    # daemon = Pyro5.server.Daemon()         # make a Pyro daemon
    # ns = Pyro5.api.locate_ns()             # find the name server
    # uri = daemon.register(Management)   # register the greeting maker as a Pyro object
    # ns.register("management", uri)   # register the object with a name in the name server
    # daemon.requestLoop()   
#     managementServer = NameServer()
#     managementServer.initDaemon()

# print("Ready.")
