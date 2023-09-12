import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time
from itertools import cycle

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("topic/confirmacao")
    

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

filename = "luminosidades.txt"

with open(filename) as file:
    lines = [line.rstrip() for line in file]


#Localizacao do MQTT broker , alterar para o endereço do broker
mqttBroker = "localhost"

#Configura um novo client, deve possuir um nome unico
client = mqtt.Client("Sensor Luz")

#Conecta ao Broker, port=1883 por padrão
client.connect(mqttBroker) 
client.on_connect = on_connect

start = time.time()

#A cada 1min manda uma mensagem com um numero aleatorio e publica


pool = cycle(lines)

for luminosidade in pool:
    
    client.publish("topic/luminosidade", luminosidade)
    print("Just published " + str(luminosidade) + " to topic luminosidade")
    time.sleep(60)

# while True:
#     randNumber = uniform(0.0, 1.0)
#     client.publish("luminosidade", randNumber)
#     print("Just published " + str(randNumber) + " to topic luminosidade")
#     time.sleep(60)