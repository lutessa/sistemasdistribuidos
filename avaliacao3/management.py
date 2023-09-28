# saved as greeting-server.py
import Pyro5.api

class Management(object):
    def __init__(self):
        self.estoque = {}
    @Pyro5.api.expose
    def register(self, name, pubKey, proxy):
        pass
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