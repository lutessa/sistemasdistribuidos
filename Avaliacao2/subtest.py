#Exemplo de Subscriber MQTT

import paho.mqtt.client as mqtt
import time
from csv import writer
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("topic/mensagens")
    


#Callback on_message
def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))


    #Guarda em um arquivo .txt a hora de recebimento da mensagem 
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    with open('horas.txt','a',newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerow([current_time])

    client.publish("topic/confirmacao","Recebeu")



mqttBroker = "localhost"

client = mqtt.Client("PCMonitor")
client.connect(mqttBroker) 


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()

