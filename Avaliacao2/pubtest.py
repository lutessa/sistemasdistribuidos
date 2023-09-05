#Exemplo de Publisher MQTT

import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("topic/confirmacao")
    
recebida = 1
def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))
    global recebida
    recebida = 0



#Localizacao do MQTT broker , alterar para o endereço do broker
mqttBroker = "localhost"

#Configura um novo client, deve possuir um nome unico
client = mqtt.Client("Udoo")

#Conecta ao Broker, port=1883 por padrão
client.connect(mqttBroker) 

#client.on_connect = on_connect

client.subscribe("topic/confirmacao")

start = time.time()

#A cada 1min manda uma mensagem com um numero aleatorio e publica
while True:
    randNumber = uniform(0.0, 100.0)
    client.publish("topic/mensagens", randNumber)
    print("Just published " + str(randNumber) + " to topic mensagens")
    #time.sleep(10)
    start = time.time()
    client.loop_start()
    #client.subscribe("topic/confirmacao")
    #while(recebida):
    client.on_message = on_message

    #end = time.time()
    #print(end-start)
    #if ((end - start) > 5):
    #    print("Mensagem nao recebida")
    #    client.loop_stop()
        
    #recebida = 0 
    #if (recebida == 0):
        #client.loop_stop()
        #recebida = 1
    time.sleep(5)
    client.loop_stop()
    if (recebida == 1):
        print("Mensagem nao recebida")
    recebida = 1

    