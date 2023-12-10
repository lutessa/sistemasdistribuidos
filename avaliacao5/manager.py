import Pyro5.api
import Pyro5.socketutil
import threading
        
class Management(object):
    def __init__(self):
        self.daemon = Pyro5.server.Daemon()
        self.uri = self.daemon.register(self)
        self.ns = Pyro5.api.locate_ns()
        self.ns.register("manager", self.uri)


        self.daemon_thread = threading.Thread(target=self.run_daemon)
        self.daemon_thread.daemon = True
        self.daemon_thread.start()


