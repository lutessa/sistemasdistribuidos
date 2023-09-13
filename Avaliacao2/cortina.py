import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

ESTADO_CORTINA = False
LUMINOSIDADE = 0.0

def on_connect(client, userdata, flags, rc):
    global ESTADO_CORTINA
    print("Connected with result code "+str(rc))
    result, mid = client.subscribe("topic/luminosidade")
    print("subscribe connection status code is", result)
    print("subscribe message id is", mid)
    result, mid = client.subscribe("topic/controle_cortina")
    print("subscribe connection status code is", result)
    print("subscribe message id is", mid)
    ESTADO_CORTINA = False
    info = client.publish("topic/estado_cortina","FECHADA")
    ##TODO: print result code
    print("publish connection status code is", info.rc)
    print("publish message id is", info.mid)

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

def on_message_luminosidade(client, userdata, message):
    global LUMINOSIDADE
    global ESTADO_CORTINA
    print("luminosidade - received message: " ,str(message.payload.decode("utf-8")))

    LUMINOSIDADE = float(message.payload.decode("utf-8"))

    if(LUMINOSIDADE <= 0.5):
        ESTADO_CORTINA = True
        info = client.publish("topic/estado_cortina","ABERTA")
        ## TODO: print result code
        print("publish connection status code is", info.rc)
        print("publish message id is", info.mid)

def on_message_controle_cortina(client, userdata, message):
    global ESTADO_CORTINA
    print("controle - received message: " ,str(message.payload.decode("utf-8")))
    msg = str(message.payload.decode("utf-8"))
    if msg == 'abra':
        ESTADO_CORTINA = True
        info = client.publish("topic/estado_cortina","ABERTA")
        ## TODO: print result code
        print("publish connection status code is", info.rc)
        print("publish message id is", info.mid)
    elif msg == 'feche':
        ESTADO_CORTINA = False
        info = client.publish("topic/estado_cortina","FECHADA")
        ## TODO: print result code
        print("publish connection status code is", info.rc)
        print("publish message id is", info.mid)
        
#Localizacao do MQTT broker , alterar para o endereço do broker
mqttBroker = "localhost"

#Configura um novo client, deve possuir um nome unico
client = mqtt.Client("cortina")

#Conecta ao Broker, port=1883 por padrão
client.connect(mqttBroker) 

client.on_connect = on_connect
client.on_message = on_message

client.message_callback_add('topic/controle_cortina', on_message_controle_cortina)
client.message_callback_add('topic/luminosidade', on_message_luminosidade)

client.loop_forever()
