import Pyro5.api
import Pyro5.socketutil
import threading
import uuid
import concurrent.futures

class Manager(object):
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
        self.transactions = {}
    def init_players(self):
        
        players_id = ["007", "008"]

        for p in players_id:
            player_proxy_uri = "PYRONAME:" + p
            player = Pyro5.api.Proxy(player_proxy_uri)
            self.players.append(player)

    @Pyro5.api.expose
    def exchange(self, player1_id, player2_id, indexes_1, indexes_2):
        print(f"Player {player1_id} requested to exchange with {player2_id} items {indexes_1} for {indexes_2}")
        print(player1_id)
        if player1_id == "007":
            # res = self.players[1].exchange_request(player1_id, indexes_1, indexes_2)
            player = Pyro5.api.Proxy("PYRONAME:008")
            res = player.exchange_request(player1_id, indexes_1, indexes_2)
            print(res)
            if res:
                self.open_trans(player1_id, player2_id, indexes_1, indexes_2)
            #return res
    def open_trans(self, player_1, player_2, idx_1, idx_2):
        TID = str(uuid.uuid4())
        print(TID)
        self.transactions[TID] = { 'status':"Exec",
                                    player_1: "waiting",
                                    player_2: "waiting"}
        print(self.transactions)
        
        p2 = Pyro5.api.Proxy(f"PYRONAME:{player_2}")
        
        p1 = Pyro5.api.Proxy(f"PYRONAME:{player_1}")
        #with Pyro5.api.Proxy(f"PYRONAME:{player_1}") as p1:

        with concurrent.futures.ThreadPoolExecutor() as executor:

            future_res1 = executor.submit(p1.exchange, TID, player_2, idx_1, idx_2)
            future_res2 = executor.submit(p2.exchange, TID, player_1, idx_2, idx_1)

            try:
                res2 = future_res2.result(timeout=30)
                self.transactions[TID][player_2] = res2
            except concurrent.futures.TimeoutError:
                res2 = "ABORT"
                self.transactions[TID][player_2] = res2
            try:
                res1 = future_res1.result(timeout=30)
                self.transactions[TID][player_1] = res1
            except concurrent.futures.TimeoutError:
                res1 = "ABORT"
                self.transactions[TID][player_1] = res1



        print(res1)
        print(res2)
        # res1 = p1.exchange(TID, player_2, idx_1, idx_2)

        # res2 = p2.exchange(TID, player_1, idx_2, idx_1)
    def run_daemon(self):
        self.daemon.requestLoop()
if __name__ == "__main__":
    manager = Manager()
    while True:
        pass