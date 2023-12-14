import Pyro5.api
import Pyro5.socketutil
import threading
import uuid
import concurrent.futures
import queue

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
        #self.init_players()
        self.transactions = {}
        self.load_transactions()
        self.transactions_queue = queue.Queue()
        self.stop_thread_flag = False
        self.queue_thread = threading.Thread(target=self.check_queue)
        self.queue_thread.start()

    def init_players(self):
        
        players_id = ["007", "008"]

        for p in players_id:
            player_proxy_uri = "PYRONAME:" + p
            proxy = Pyro5.api.Proxy(player_proxy_uri)
            player = {"id": p, "proxy": proxy}
            self.players.append(player)
    def load_transactions(self):
        log_file = "manager_log.txt"
        with open(log_file, 'r') as file:
            for line in file:
                parts = line.strip().split()

                if len(parts) == 4:
                    tid, status, player, answer = parts
                    if tid not in self.transactions:
                        self.transactions[tid] = {'status': status}
                    else:
                        self.transactions[tid]['status'] = status
                    self.transactions[tid][player] = answer
                elif len(parts) == 2:
                    tid, status = parts
                    if tid not in self.transactions:
                        self.transactions[tid] = {'status': status}
                    else:
                        self.transactions[tid]['status'] = status
        print(self.transactions)

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
                #self.open_trans(player1_id, player2_id, indexes_1, indexes_2)
                self.transactions_queue.put([player1_id, player2_id, indexes_1, indexes_2])
            player._pyroRelease
            #return res
    @Pyro5.api.expose
    def get_Decision(self, TID):
        status = self.transactions[TID]['status']
        return status
    def check_queue(self):
        while not self.stop_thread_flag:
            try:
                player_1, player_2, idx_1, idx_2 = self.transactions_queue.get(block=True)
                self.open_trans(player_1, player_2, idx_1, idx_2)
            except queue.Empty:
                pass
    def stop_thread(self):
        self.stop_thread_flag = True
        self.queue_thread.join()
    def open_trans(self, player_1, player_2, idx_1, idx_2):
        TID = str(uuid.uuid4())
        #print(TID)
        self.transactions[TID] = { 'status':"Exec",
                                    player_1: "waiting",
                                    player_2: "waiting"}
        #print(self.transactions)
        
        log_file = "manager_log.txt"
        with open(log_file, 'a') as f:
            f.write(f'{TID} Exec {player_1} waiting\n')
            f.write(f'{TID} Exec {player_2} waiting\n')

        


        with concurrent.futures.ThreadPoolExecutor() as executor:
            p1 = Pyro5.api.Proxy(f"PYRONAME:{player_1}")
            p1._pyroClaimOwnership()

            p2 = Pyro5.api.Proxy(f"PYRONAME:{player_2}")
            p2._pyroClaimOwnership()

            def exchange_with_timeout(proxy, tid, player, other_player, indexes_1, indexes_2):
                try:
                    proxy._pyroClaimOwnership()
                    result = proxy.exchange(tid, other_player, indexes_1, indexes_2)
                    self.transactions[tid][player] = result
                    log_file = "manager_log.txt"
                    with open(log_file, 'a') as f:
                        f.write(f'{TID} Exec {player} {result}\n')
            
        
                    return result
                except concurrent.futures.TimeoutError:
                    result = "ABORT"
                    self.transactions[tid][player] = result
                    log_file = "manager_log.txt"
                    with open(log_file, 'a') as f:
                        f.write(f'{TID} Exec {player} {result}')
            

                    return result

            future_res1 = executor.submit(exchange_with_timeout, p1, TID, player_1, player_2, idx_1, idx_2)
            future_res2 = executor.submit(exchange_with_timeout, p2, TID, player_2, player_1, idx_2, idx_1)


            res1 = future_res1.result(timeout=30)
            res2 = future_res2.result(timeout=30)


                
            print(res1)
            print(res2)

            if res1=="READY" and res2=='READY':
                p1._pyroClaimOwnership()
                p2._pyroClaimOwnership()
                p1.complete_trans(TID)
                p2.complete_trans(TID)
                self.transactions[TID]['status'] = "COMPLETED"
                log_file = "manager_log.txt"
                with open(log_file, 'a') as f:
                    f.write(f'{TID} COMPLETED\n')
                
            else:
                self.transactions[TID]['status'] = "ABORT"
                with open(log_file, 'a') as f:
                    f.write(f'{TID} ABORT\n')
    def run_daemon(self):
        self.daemon.requestLoop()
if __name__ == "__main__":
    manager = Manager()
    while True:
        pass