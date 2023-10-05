import Pyro5.api
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import threading 

class client(object):
    def __init__(self, manager_uri):
        self.manager = Pyro5.api.Proxy(manager_uri)
        daemon = Pyro5.api.Daemon()      # make a Pyro daemon
        uri = daemon.register(client)    # register the client as a Pyro object
        client_thread = threading.Thread(target=daemon.requestLoop, args=(1,))
        client_thread.start()
        self.manager.register(self.name, self.pub_key, self.uri)
    
    @Pyro5.api.expose
    @Pyro5.api.callback
    def min_stock(self, item):
        print(item)

    @Pyro5.api.expose
    @Pyro5.api.callback
    def not_sold_report(self, items):
        print(items)


def create_pair_key():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()

    private_pem = private_key.export_key().decode()
    public_pem = public_key.export_key().decode()
    with open('private_pem.pem', 'w') as pr:
        pr.write(private_pem)
    with open('public_pem.pem', 'w') as pu:
        pu.write(public_pem)


