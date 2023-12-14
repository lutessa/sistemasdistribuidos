import Pyro5.api
import Pyro5.socketutil
import threading
import time
class Player:
    def __init__(self, player_id):
        manager_uri = "PYRONAME:manager"
        self.player_id = player_id
        self.partner_id = -1
        self.file_name = f"{player_id}.txt"
        self.objects = self.load_objects()

        self.manager = Pyro5.api.Proxy(manager_uri)
        self.daemon = Pyro5.api.Daemon()    
        self.uri = self.daemon.register(self) 
        self.ns = Pyro5.api.locate_ns()
        self.ns.register(player_id, self.uri)
        self.client_thread = threading.Thread(target=self.daemon.requestLoop)
        self.client_thread.start()

        self.check_log()

    def load_objects(self):
        try:
            with open(self.file_name, "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"O arquivo {self.file_name} não foi encontrado.")
            return []

    def list_objects(self):
        print(f"------ Player {self.player_id} Objects ------------")
        for i, obj in enumerate(self.objects):
            print(f"{i} - {obj}")

    def list_other_player_objects(self, other_player_id):
        try:
            with open(f"{other_player_id}.txt", "r") as file:
                objects = [line.strip() for line in file.readlines()]
                print(f"----- Player {other_player_id} Objects ------------")
                for i, obj in enumerate(objects):
                    print(f"{i} - {obj}")
        except FileNotFoundError:
            print(f"O arquivo do Player {other_player_id} não foi encontrado.")

    def request_exchange(self, other_player_id, indexes_1, indexes_2):
        res = self.manager.exchange(self.player_id, other_player_id, indexes_1, indexes_2)
        # if res:
        #     objects = []
        #     with open(f"{other_player_id}.txt", "r") as file:
        #         objects = [line.strip() for line in file.readlines()]
        #     #self.exchange(indexes_1, indexes_2, objects)

    @Pyro5.api.expose
    @Pyro5.api.callback
    def exchange(self, TID, other_player_id, my_indexes, other_indexes):

        try:
            accept = input("Type 1 to accept")
            if int(accept) == 1:
                pass
            else:
                raise ValueError("")

            log_file = self.player_id + "_log.txt"
            log = f"{TID} exec {other_player_id} {my_indexes} {other_indexes}"
            with open(log_file, 'a') as f:
                f.write(log + '\n')
            other_list = []
            with open(f"{other_player_id}.txt", "r") as file:
                other_list = [line.strip() for line in file.readlines()]
            #print(other_list)
            new_objects = self.objects
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
                f.close()

            log_file = self.player_id + "_log.txt"
            log = f"{TID} ready {other_player_id} {my_indexes} {other_indexes}"
            with open(log_file, 'a') as f:
                f.write(log + '\n')
            return "READY"
        except Exception as e:
            print(e)

            log_file = self.player_id + "_log.txt"
            log = f"{TID} failed {other_player_id} {my_indexes} {other_indexes}"
            with open(log_file, 'a') as f:
                f.write(log + '\n')

            return "ABORT"

    @Pyro5.api.expose
    @Pyro5.api.callback
    def complete_trans(self, TID):
        self.save_temp_to_final(TID)



    def save_temp_to_final(self, TID):
    def save_temp_to_final(self, TID):
        temp_file = self.player_id + "_temp.txt"
        final_file = self.player_id + ".txt"
        with open(temp_file, 'r') as temp:
            data = temp.read()

        with open(final_file, 'w') as final:
            final.write(data)

        log_file = self.player_id + "_log.txt"
        log = f"{TID} completed"
        with open(log_file, 'a') as f:
            f.write(log + '\n')
        print(log)
        print(data)

    def check_log(self):
        log_file = self.player_id + "_log.txt"
        with open(log_file, 'r') as f:
            l = f.readlines()
            if l:
                last_line = l[-1].strip().split()

                if len(last_line)>=2:
                    id = last_line[0]
                    status = last_line[1]

                    if status != "completed":
                        res = self.manager.get_Decision(id)
                        if res == "COMPLETED":
                            self.save_temp_to_final(id)
    @Pyro5.api.expose
    @Pyro5.api.callback
    def exchange_request(self, other_player_id, indexes_1, indexes_2):
        other_player_objs = []
        with open(other_player_id+".txt", "r") as file:
            other_player_objs = [line.strip() for line in file.readlines()]            
    
        my_objs = [self.objects[idx] for idx in indexes_2]
        their_objs = [other_player_objs[idx] for idx in indexes_1]

        print(f"Player {other_player_id} requested to exchange items {my_objs} for {their_objs}")

        res = input("1 to accept, else to decline")
        return res == '1'

def display_menu(menu, player):
    print("----------- Menu Selection -----------------")
    for key, function in menu.items():
        print(key, "-", function.__name__)

def list_items(player):
    player.list_objects()

def set_partner(player):
    partner_id = input("Enter partner id:\n")
    player.partner_id = partner_id

def list_partner_items(player):
    if player.partner_id == -1:
        print("Partner was not set!\n")
    else:
        player.list_other_player_objects(player.partner_id)

def list_both_items(player):
    if player.partner_id == -1:
        print("Partner was not set!\n")
    else:
        player.list_objects()
        player.list_other_player_objects(player.partner_id)

def request_exchange(player):
    if player.partner_id == -1:
        print("Partner was not set!\n")
    else:
        my_item = int(input("Enter item from own list to exchange:\n"))
        their_item = int(input("Enter item from partner's list to exchange:\n"))
        player.request_exchange(player.partner_id, [my_item],[their_item])   

def received_exchange_request(player):
    time.sleep(3)

def clear_screen(player):
    system('clear')

def done(player):
    system('clear')  # clears stdout
    print("Goodbye")
    return

def menu_init(player):
    functions_names = [list_items, set_partner, list_partner_items, list_both_items, request_exchange, received_exchange_request, clear_screen, done]
    menu_items = dict(enumerate(functions_names, start=1))

    while True:
        display_menu(menu_items, player)
        selection = int(
            input("Please enter your selection number: "))  # Get function key
        selected_value = menu_items[selection]  # Gets the function name
        selected_value(player)  # add parentheses to call the function

if __name__ == "__main__":

    player_id = input("Digite o seu Player ID: ")
    player = Player(player_id)

    player.list_objects()

    if player_id == "007":
        while True:
            player.list_other_player_objects("008")
            items_to_give = input("Type items to give: ").split(',')
            items_to_receive = input("Type items to receive: ").split(',')


            indexes_to_give = [int(index) for index in items_to_give]
            indexes_to_receive = [int(index) for index in items_to_receive]

            player.request_exchange(indexes_to_give, indexes_to_receive)
            time.sleep(60)