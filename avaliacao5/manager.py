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
        self.players = []
        self.init_players()

    def init_players(self):
        
        players_id = ["007", "008"]

        for p in players_id:
            player_proxy_uri = "PYRONAME:" + p
            player = Pyro5.api.Proxy(player_proxy_uri)
            self.players.append(player)

    @Pyro5.api.expose
    def exchange(self, player1_id, player2_id, indexes_1, indexes_2):
        pass