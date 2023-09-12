import tkinter as tk
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("topic/confirmacao")
    
def on_message(client, userdata, message):
    print(f"Mensagem recebida no tópico {message.topic}: {message.payload.decode('utf-8')}")

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

def on_message_estado_led(client, userdata, message):
    global ESTADO_LED
    print("controle - received message: " ,str(message.payload.decode("utf-8")))

    msg = str(message.payload.decode("utf-8"))
    if msg == 'ligue':
        ESTADO_LED = True
        client.publish("topic/estado_led","LIGADO")
        ## TODO: print result code
    elif msg == 'desligue':
        ESTADO_LED = False
        client.publish("topic/estado_led","DESLIGADO")
        ## TODO: print result code
        

def on_message_luminosidade(client, userdata, message):
    global LUMINOSIDADE
    global ESTADO_CORTINA
    global ESTADO_LED
    print("luminosidade - received message: " ,str(message.payload.decode("utf-8")))


    LUMINOSIDADE = float(message.payload.decode("utf-8"))

    if LUMINOSIDADE < 0.5 and ESTADO_CORTINA:
        ESTADO_LED = True
        client.publish("topic/estado_led","LIGADO")
        ## TODO: print result code        


def button_luminosidade_callback():
    client.subscribe("topic/luminosidade")



def button_led_callback():
    client.subscribe("topic/estado_led")


def button_cortina_callback():
    client.subscribe("topic/estado_cortina")

def ligar_led_callback():
    client.publish("topic/controle_led", "ligue")

def desligar_led_callback():
    client.publish("topic/controle_led", "desligue")

def abrir_cortina_callback():
    client.publish("topic/controle_cortina", "abra")

def fechar_cortina_callback():
    client.publish("topic/controle_cortina", "feche")


#Localizacao do MQTT broker , alterar para o endereço do broker
mqttBroker = "localhost"


#Configura um novo client, deve possuir um nome unico
client = mqtt.Client("USER")


#Conecta ao Broker, port=1883 por padrão
client.connect(mqttBroker) 
client.on_connect = on_connect


root = tk.Tk()
root.title("MQTT")


button1 = tk.Button(root, text="Sub topico luminosidade", command=button_luminosidade_callback)
button1.pack()

button2 = tk.Button(root, text="Sub topico led", command=button_led_callback)
button2.pack()

button3 = tk.Button(root, text="Sub topico cortina", command=button_cortina_callback)
button3.pack()


ligar_led = tk.Button(root, text="Ligar", command=ligar_led_callback)
ligar_led.pack()

desligar_led = tk.Button(root, text="Desligar", command=desligar_led_callback)
desligar_led.pack()

abrir_cortina = tk.Button(root, text="Abrir", command=abrir_cortina_callback)
abrir_cortina.pack()

fechar_cortina = tk.Button(root, text="Fechar", command=fechar_cortina_callback)
fechar_cortina.pack()

root.mainloop()




client.on_message = on_message


client.loop_forever()
