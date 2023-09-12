import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

ESTADO_CORTINA = False
LUMINOSIDADE = 0.0

def on_connect(client, userdata, flags, rc):
    global ESTADO_CORTINA
    print("Connected with result code "+str(rc))
    client.subscribe("topic/luminosidade")
    client.subscribe("topic/controle_cortina")

    ESTADO_CORTINA = False
    client.publish("topic/estado_cortina","FECHADA")
    
    ##TODO: print result code

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

def on_message_luminosidade(client, userdata, message):
    global LUMINOSIDADE
    global ESTADO_CORTINA
    print("luminosidade - received message: " ,str(message.payload.decode("utf-8")))

    LUMINOSIDADE = float(message.payload.decode("utf-8"))

    if(LUMINOSIDADE <= 0.5):
        ESTADO_CORTINA = True
        client.publish("topic/estado_cortina","ABERTA")
        ## TODO: print result code


def on_message_controle_cortina(client, userdata, message):
    global ESTADO_CORTINA
    print("controle - received message: " ,str(message.payload.decode("utf-8")))
    msg = str(message.payload.decode("utf-8"))
    if msg == 'abra':
        ESTADO_CORTINA = True
        client.publish("topic/estado_cortina","ABERTA")
        ## TODO: print result code
    elif msg == 'feche':
        ESTADO_CORTINA = False
        client.publish("topic/estado_cortina","FECHADA")
        ## TODO: print result code
        



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
