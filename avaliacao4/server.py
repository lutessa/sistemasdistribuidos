from flask import Flask,jsonify, request
from flask_sse import sse
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
#import datetime
from helper import get_data,get_schd_time
from datetime import datetime, timedelta
estoque = {}
app = Flask(__name__)
CORS(app)
#CORS(app, resources={"/events": {"origins": "file://"}})
#CORS(app, resources={r"/events": {"origins": "http://localhost:8080"}})
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/events')
log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

def notSoldReport():
    notSold = []
    current_time = datetime.now()
    time_limite = current_time - timedelta(minutes=2)

    for code in estoque:

        last_remove_time = estoque[code]["last_remove_time"]
        if last_remove_time != 0:

            if isinstance(last_remove_time, str):
                last_remove_time = datetime.strptime(last_remove_time, '%Y-%m-%d %H:%M:%S.%f')
            if isinstance(last_remove_time, datetime):
                last_remove_timestamp = int(last_remove_time.timestamp())
                if last_remove_timestamp < int(time_limite.timestamp()):
                    notSold.append(estoque[code]['name'])
        else:
            last_insert_time = estoque[code]["last_insert_time"]
            if isinstance(last_insert_time, str):
                last_insert_time = datetime.strptime(last_insert_time, '%Y-%m-%d %H:%M:%S.%f')
            if isinstance(last_insert_time, datetime):
                last_insert_timestamp = int(last_insert_time.timestamp())
                if last_insert_timestamp < int(time_limite.timestamp()):
                    notSold.append(estoque[code]['name'])
    print(notSold)
    return notSold
def server_side_event():
    """ Function to publish server side event """
    with app.app_context():
        #sse.publish("ameba", type='randomtype')
        sse.publish(notSoldReport(), type='dataUpdate')
        #sse.publish(get_data(), type='dataUpdate')
        print("Event Scheduled at ",datetime.now())


# sched = BackgroundScheduler(daemon=True)
# sched.add_job(server_side_event,'interval',seconds=get_schd_time())
# sched.start()

@app.route('/insert', methods=["POST"])
def insert_item():
    data = request.get_json()
    
    current_time = datetime.now()

    code = data['code']
    name = data["name"]
    description = data["description"]
    price = data["price"]
    minStorage = int(data['minStorage'])
    qnt = int(data['qnt'])

    print(data)
    if code in estoque:
        estoque[code]["name"] = name
        estoque[code]["description"] = description
        estoque[code]["price"] = price
        estoque[code]["minStorage"] = minStorage
        estoque[code]["qnt"] += qnt
        estoque[code]["last_insert_time"] = current_time

        return "Objeto inserido com sucesso"
    else:
        estoque[code] = {
                            "name": name,
                            "description": description,
                            "price": price,
                            "minStorage": minStorage,
                            "qnt": qnt,
                            "last_insert_time": current_time,
                            "last_remove_time": datetime.fromtimestamp(0)
                        }
        return "Novo objeto adicionado com sucesso"

    #return "OK"

@app.route('/remove', methods=["POST"])
def remove_item():
    data = request.get_json()
    #data = request.json()
    print(data)

    current_time = datetime.now()

    code = data['code']
    qnt = int(data['qnt'])

    if code in estoque:
        #if amount to remove is bigger than existing
        if qnt > estoque[code]["qnt"]:
            print('O estoque é insuficiente para ser retirada a quantidade pedida')
            return "ERROR: O estoque é insuficiente para ser retirada a quantidade pedida"
        if estoque[code]["qnt"]-qnt < estoque[code]["minStorage"]:
            print("sending flag")
            sse.publish(f"Estoque minimo de {estoque[code]['name']} atingido", type='dataUpdate')
            estoque[code]["last_remove_time"] = current_time
            return "1: Operação concluída, objeto no limite"
        estoque[code]["qnt"] -= qnt
        estoque[code]["last_remove_time"] = current_time  
        return "0: Operação concluída"
    else:
        print('O item requerido não está disponível')
        return 'ERROR: O item requerido não está disponível'
    

    #return "OK"



if __name__ == '__main__':
   app.run(debug=True,host='0.0.0.0',port=5000)