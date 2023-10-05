import Pyro5.api
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

class User():
    def __init__(self, name, pub_key, remote_obj):
        self.name = name
        self.pub_key = pub_key
        self.remote_obj = remote_obj
        
class Management(object):
    def __init__(self):
        self.estoque = {}
        self.users = []
    @Pyro5.api.expose
    def register(self, name, pubKey, uri):
        user_proxy = Pyro5.api.Proxy(uri)
        ### if user name pub ! exists
        self.users.append(User(name,pub_key,user_proxy ))
    def checkKey(self):
        pass
    #TODO: tratar entrada no cliente
    @Pyro5.api.expose
    def insertItem(self, code, name, description, qnt, price, minStorage):
        if not self.checkKey():
            return "ERROR"

        if code in self.estoque:
            self.estoque[code]["name"] = name
            self.estoque[code]["description"] = description
            self.estoque[code]["price"] = price
            self.estoque[code]["qnt"] += qnt
        else:
            self.estoque[code]["name"] = name
            self.estoque[code]["description"] = description
            self.estoque[code]["price"] = price
            self.estoque[code]["qtn"] = qnt

        return "Success"

    @Pyro5.api.expose
    def removeItem(self, code, qnt):
        if not self.checkKey():
            return "ERROR"
        
        if code in self.estoque:
            if qnt > self.estoque[code]["qnt"]:
                #TODO: eniar flag estoque min p client
                for user in users:
                    user.remote_obj.min_stock(self.estoque[code]["name"])
                return "error"
            self.estoque[code]["qnt"] -= qnt
    def getReport(self):
        pass


    def get_fortune(self, name):
        return "Hello, {0}. Here is your fortune message:\n" \
               "Tomorrow's lucky number is 12345678.".format(name)

if __name__ == "__main__":

    daemon = Pyro5.server.Daemon()         # make a Pyro daemon
    ns = Pyro5.api.locate_ns()             # find the name server
    uri = daemon.register(Management)   # register the greeting maker as a Pyro object
ns.register("example.greeting", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()   