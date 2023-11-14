from flask import Flask,jsonify, request
from flask_sse import sse
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
import json
#import datetime
from helper import get_schd_time #get_data,
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

    current_timestamp = int(current_time.timestamp())
    
    for code in estoque:

        last_remove_time = estoque[code]["last_remove_time"]
        last_remove_timestamp = int(last_remove_time.timestamp())

        if last_remove_timestamp != 946695600:  #0

            if (current_timestamp - int(last_remove_timestamp)) > 120:
                print(code)
                notSold.append(estoque[code]['name'])
        else:
            last_insert_time = estoque[code]["last_insert_time"]
            last_insert_timestamp = int(last_insert_time.timestamp())

            if (current_timestamp - last_insert_timestamp) > 120:
                print(code)
                notSold.append(estoque[code]['name'])
        print('notSold:', notSold)
        print(estoque)
        return notSold

def server_side_event():
    """ Function to publish server side event """
    with app.app_context():
        notSoldList = notSoldReport()
        if notSoldList:
            sse.publish(notSoldReport(), type='dataUpdate')
            print("Event Scheduled at ",datetime.now())


sched = BackgroundScheduler(daemon=True)
sched.add_job(server_side_event,'interval',seconds=get_schd_time())
sched.start()

@app.route('/insert', methods=["POST"])
def insert_item():
    data = request.get_json()
    # data = json.loads(data)
    
    current_time = datetime.now()

    code = data['code']
    name = data["name"]
    description = data["description"]
    price = data["price"]
    minStorage = data['minStorage']
    qnt = int(data['qnt'])

    print(data)
    if code in estoque:
        estoque[code]["name"] = name
        estoque[code]["description"] = description
        estoque[code]["price"] = price
        estoque[code]["minStorage"] = minStorage
        estoque[code]["qnt"] += int(qnt)
        estoque[code]["last_insert_time"] = current_time
        print(estoque[code]['qnt'])
        return "Objeto inserido com sucesso"
    else:
        estoque[code] = {
                            "name": name,
                            "description": description,
                            "price": price,
                            "minStorage": minStorage,
                            "qnt": qnt,
                            "last_insert_time": current_time,
                            "last_remove_time": datetime(2000,1,1)#datetime.fromtimestamp(0)
                        }
        print("Novo objeto adicionado com sucesso")

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
        if (qnt > estoque[code]["qnt"]):
            print('O estoque é insuficiente para ser retirada a quantidade pedida')
            return "ERROR: O estoque é insuficiente para ser retirada a quantidade pedida"
        if (estoque[code]["qnt"])-qnt < int(estoque[code]["minStorage"]):
            print("sending flag")
            sse.publish(f"Estoque minimo de {estoque[code]['name']} atingido", type='warningUpdate')
            estoque[code]["last_remove_time"] = current_time
            # return "1: Operação concluída, objeto no limite"
        estoque[code]["qnt"] -= qnt
        estoque[code]["last_remove_time"] = current_time  
        return "0: Operação concluída"
    else:
        print('O item requerido não está disponível')
        return 'ERROR: O item requerido não está disponível'
    
@app.route('/estoque', methods=['GET'])
def emEstoque():
    emEstoque = []

    for code in estoque:
        if estoque[code]['qnt'] > 0:
            product = {"code": code,
                       "name": estoque[code]['name'],
                       "qnt": estoque[code]['qnt']}
            emEstoque.append(product)
    print(emEstoque)
    return jsonify(emEstoque)


@app.route('/semsaida', methods=['POST'])
def semSaida():
    data_inicial = request.form.get('dataInicial')
    hora_inicial = request.form.get('horaInicial')
    data_final = request.form.get('dataFinal')
    hora_final = request.form.get('horaFinal')

    periodoInicial = datetime.strptime(f'{data_inicial} {hora_inicial}', '%Y-%m-%d %H:%M')
    periodoFinal = datetime.strptime(f'{data_final} {hora_final}', '%Y-%m-%d %H:%M')
    
    print(periodoInicial)
    print(periodoFinal)

    items = []
    periodoInicial_timestamp = periodoInicial.timestamp()

    for code in estoque:
        last_remove_time = estoque[code]["last_remove_time"]
        last_remove_timestamp = last_remove_time.timestamp()

        if (last_remove_timestamp == 946695600) or (last_remove_timestamp < periodoInicial_timestamp):  #last_remove_time == 0
            product = {"code": code,
                       "name": estoque[code]['name'],
                       "last_remove_time": estoque[code]["last_remove_time"]}

            items.append(product)
    print(items)
    return items


@app.route('/fluxo', methods=['POST'])
def fluxoPorPeriodo():
    data_inicial = request.form.get('dataInicial')
    hora_inicial = request.form.get('horaInicial')
    data_final = request.form.get('dataFinal')
    hora_final = request.form.get('horaFinal')

    periodoInicial = datetime.strptime(f'{data_inicial} {hora_inicial}', '%Y-%m-%d %H:%M')
    periodoFinal = datetime.strptime(f'{data_final} {hora_final}', '%Y-%m-%d %H:%M')
    
    print(periodoInicial)
    print(periodoFinal)

    items = [] 

    periodoInicial_timestamp = periodoInicial.timestamp()
    periodoFinal_timestamp = periodoFinal.timestamp()

    for code in estoque:
        last_insert_timestamp = estoque[code]["last_insert_time"].timestamp()

        last_remove_timestamp = estoque[code]["last_remove_time"].timestamp()

        if (((last_remove_timestamp > periodoInicial_timestamp) and (last_remove_timestamp < periodoFinal_timestamp)) or ((last_insert_timestamp > periodoInicial_timestamp) and (last_insert_timestamp < periodoFinal_timestamp))):
            product = {"code": code,
                       "name": estoque[code]['name'],
                       "last_insert_time": estoque[code]["last_insert_time"],
                       "last_remove_time": estoque[code]["last_remove_time"]}

            items.append(product)
    print(items)
    return items
    #return "0"

if __name__ == '__main__':
   app.run(debug=True,host='0.0.0.0',port=5000)
