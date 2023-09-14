import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

LUMINOSIDADE = 0.0
ESTADO_CORTINA = False
ESTADO_LED = False
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    result, mid = client.subscribe("topic/estado_cortina")
    print("subscribe 'estado_cortina' connection status code is", result)
    print("subscribe message id is", mid)
    result, mid = client.subscribe("topic/controle_led")
    print("subscribe 'controle_led' connection status code is", result)
    print("subscribe message id is", mid)
    result, mid = client.subscribe("topic/luminosidade")
    print("subscribe 'luminosidade' connection status code is", result)
    print("subscribe message id is", mid)
    
    ##TODO: print result code

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

def on_message_estado_cortina(client, userdata, message):
    global ESTADO_CORTINA
    print("estado cortina - received message: " ,str(message.payload.decode("utf-8")))

    msg = str(message.payload.decode("utf-8"))
    if msg == 'ABERTA':
        ESTADO_CORTINA = True

        ## TODO: print result code
    elif msg == 'FECHADA':
        ESTADO_CORTINA = False
        ## TODO: print result code

def on_message_controle_led(client, userdata, message):
    global ESTADO_LED
    print("controle - received message: " ,str(message.payload.decode("utf-8")))

    msg = str(message.payload.decode("utf-8"))
    if msg == 'ligue':
        ESTADO_LED = True
        info = client.publish("topic/estado_led","LIGADO")
        ## TODO: print result code
        print("publish 'LIGADO' connection status code is", info.rc)
        print("publish 'LIGADO' message id is", info.mid)
    elif msg == 'desligue':
        ESTADO_LED = False
        info = client.publish("topic/estado_led","DESLIGADO")
        ## TODO: print result code
        print("publish 'DESLIGADO' connection status code is", info.rc)
        print("publish 'DESLIGADO' message id is", info.mid)
        
def on_message_luminosidade(client, userdata, message):
    global LUMINOSIDADE
    global ESTADO_CORTINA
    global ESTADO_LED
    print("luminosidade - received message: " ,str(message.payload.decode("utf-8")))

    LUMINOSIDADE = float(message.payload.decode("utf-8"))

    if LUMINOSIDADE < 0.5 and ESTADO_CORTINA:
        ESTADO_LED = True
        info = client.publish("topic/estado_led","LIGADO")
        ## TODO: print result code        
        print("publish 'LIGADO' connection status code is", info.rc)
        print("publish 'LIGADO' message id is", info.mid)

#Localizacao do MQTT broker , alterar para o endereço do broker
mqttBroker = "localhost"

#Configura um novo client, deve possuir um nome unico
client = mqtt.Client("LED")

#Conecta ao Broker, port=1883 por padrão
client.connect(mqttBroker) 

client.on_connect = on_connect

client.message_callback_add('topic/estado_cortina', on_message_estado_cortina)
client.message_callback_add('topic/controle_led', on_message_controle_led)
client.message_callback_add('topic/luminosidade', on_message_luminosidade)

client.on_message = on_message

client.loop_forever()
