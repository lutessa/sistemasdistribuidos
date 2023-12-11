import Pyro5.api
import Pyro5.socketutil
import threading

class Player:
    def __init__(self, player_id):
        manager_uri = "PYRONAME:manager"
        self.player_id = player_id
        self.file_name = f"{player_id}.txt"
        self.objects = self.load_objects()

        self.manager = Pyro5.api.Proxy(manager_uri)
        self.daemon = Pyro5.api.Daemon()    
        self.uri = self.daemon.register(self) 
        self.ns = Pyro5.api.locate_ns()
        self.ns.register(player_id, self.uri)

        self.check_log()

    def load_objects(self):
        try:
            with open(self.file_name, "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"O arquivo {self.file_name} não foi encontrado.")
            return []

    def list_objects(self):
        print(f"Objetos do Player {self.player_id}:")
        for i, obj in enumerate(self.objects):
            print(f"{i} {obj}")

    def list_other_player_objects(self, other_player_id):
        try:
            with open(f"{other_player_id}.txt", "r") as file:
                objects = [line.strip() for line in file.readlines()]
                print(f"Objetos do Player {other_player_id}:")
                for obj in objects:
                    print(obj)
        except FileNotFoundError:
            print(f"O arquivo do Player {other_player_id} não foi encontrado.")

    def request_exchange(self, my_player_id, other_player_id, indexes_1, indexes_2):
        res = self.manager.exchange(my_player_id, other_player_id, indexes_1, indexes_2)
        pass

    def exchange(self, my_indexes, other_indexes, other_list):
        
        try:
            new_objects = self.list_objects
            objects_1 = [new_objects[indice] for indice in my_indexes]
            objects_2 = [other_list[indice] for indice in other_indexes]

            for indice in sorted(my_indexes, reverse=True):
                del new_objects[indice]
            for indice in sorted(other_indexes, reverse=True):
                del other_list[indice]

            new_objects.extend(objects_2)
            other_list.extend(objects_1)

            with open(self.player_id + "_temp.txt", 'w') as f:
                for item in new_objects:
                    f.write(str(item) + '\n')

            #TODO return to manager efetivação provisória
        except:
            #TODO return to manager falha
            pass

    def save_temp_to_final(self):
        temp_file = self.player_id + "_temp.txt"
        final_file = self.player_id + ".txt"
        with open(temp_file, 'r') as temp:
            data = temp.read()

        with open(final_file, 'w') as final:
            final.write(data)
        #TODO write on log

    #TODO: check if theres an unfinished transaction and ask manager for result
    def check_log(self):
        log_file = self.player_id + "_log.txt"
        pass

    @Pyro5.api.expose
    @Pyro5.api.callback
    def exchange_request(self, other_player_id, indexes_1, indexes_2):
        pass
if __name__ == "__main__":

    player_id = input("Digite o seu Player ID: ")

    player = Player(player_id)

    player.list_objects()

    friend_id = input("Digite o ID do seu ammigo: ")

    
    player.list_other_player_objects(friend_id)
