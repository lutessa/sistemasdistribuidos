import tkinter as tk
import paho.mqtt.client as mqtt
from tkinter import Scrollbar
import threading
LUMINOSIDADE = 1.0
ESTADO_CORTINA = False
ESTADO_LED = False


def exibir_resultado(mensagem):
    resultado_text.config(state=tk.NORMAL)  
    resultado_text.insert(tk.END, mensagem + "\n")  
    resultado_text.see(tk.END)  
    resultado_text.config(state=tk.DISABLED)  

def publish(topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
        exibir_resultado(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
        exibir_resultado(f"Failed to send message to topic {topic}")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("topic/confirmacao")
    
def on_subscribe(client, userdata, mid, granted_qos):
    topic = userdata[(granted_qos[0], mid)]
    if topic:
        print(f"Subscribed to topic {topic} wih QoS: {granted_qos[0]}")
        exibir_resultado(f"Subscribed to topic {topic} with QoS: {granted_qos[0]}")

def on_sub_cortina(mosq, obj, mid, granted_qos):
    print("Subscribed to topic/estado_cortina: " + str(mid) + " " + str(granted_qos))
    exibir_resultado("Subscribed to topic/estado_cortina: " + str(mid) + " " + str(granted_qos))
    
def on_sub_led(mosq, obj, mid, granted_qos):
    print("Subscribed to topic/estado_led: " + str(mid) + " " + str(granted_qos))
    exibir_resultado("Subscribed to topic/estado_led: " + str(mid) + " " + str(granted_qos))

def on_sub_luminosidade(mosq, obj, mid, granted_qos):
    print("Subscribed to topic/luminosidade: " + str(mid) + " " + str(granted_qos))
    exibir_resultado("Subscribed to topic/luminosidade: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, message):
    print(f"Mensagem recebida no tópico {message.topic}: {message.payload.decode('utf-8')}")

def on_message_estado_cortina(client, userdata, message):
    global ESTADO_CORTINA
    print("estado cortina - received message: " ,str(message.payload.decode("utf-8")))
    msg = str(message.payload.decode("utf-8"))
    exibir_resultado(f"estado cortina - received message: {msg}" )
    msg = str(message.payload.decode("utf-8"))
    if msg == 'ABERTA':
        ESTADO_CORTINA = True
    elif msg == 'FECHADA':
        ESTADO_CORTINA = False
def on_message_estado_led(client, userdata, message):
    global ESTADO_LED
    print("controle - received message: " ,str(message.payload.decode("utf-8")))
    msg = str(message.payload.decode("utf-8"))
    exibir_resultado(f"controle - received message: {msg}")
    msg = str(message.payload.decode("utf-8"))
    if msg == 'ligue':
        ESTADO_LED = True
        publish("topic/estado_led","LIGADO")

    elif msg == 'desligue':
        ESTADO_LED = False
        publish("topic/estado_led","DESLIGADO")

def on_message_luminosidade(client, userdata, message):
    global LUMINOSIDADE
    global ESTADO_CORTINA
    global ESTADO_LED
    print("luminosidade - received message: " ,str(message.payload.decode("utf-8")))
    msg = str(message.payload.decode("utf-8"))
    exibir_resultado(f"luminosidade - received message: {msg}")
    LUMINOSIDADE = float(message.payload.decode("utf-8"))

def button_luminosidade_callback():
    topic = "topic/luminosidade"
    mid = client.subscribe(topic)
    client.user_data_set({mid: topic})

    client.message_callback_add('topic/luminosidade', on_message_luminosidade)

def button_led_callback():
    # client.subscribe("topic/estado_led")
    topic = "topic/estado_led"
    mid = client.subscribe(topic)
    client.user_data_set({mid: topic})

    client.message_callback_add('topic/estado_led', on_message_estado_led)  
    #client.subscribe_callback_add('topic/estado_led', on_sub_led)

def button_cortina_callback():
    # client.subscribe("topic/estado_cortina")

    topic = "topic/estado_cortina"
    mid = client.subscribe(topic)
    client.user_data_set({mid: topic})
    client.message_callback_add('topic/estado_cortina', on_message_estado_cortina)
    # mensagem = f"Subscribed to topic topic/estado_cortina"
    #client.subscribe_callback_add('topic/estado_cortina', on_sub_cortina)

def ligar_led_callback():
    publish("topic/controle_led", "ligue")

def desligar_led_callback():
    publish("topic/controle_led", "desligue")

def abrir_cortina_callback():
    publish("topic/controle_cortina", "abra")

def fechar_cortina_callback():
    publish("topic/controle_cortina", "feche")

def mqtt_loop():
    client.on_message = on_message
    client.loop_forever()

mqttBroker = "localhost"

client = mqtt.Client("USER")

client.connect(mqttBroker) 
client.on_connect = on_connect

client.on_subscribe = on_subscribe

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True  
mqtt_thread.start()

root = tk.Tk()
root.geometry("600x600")
root.title("MQTT")
root.config(padx=10, pady=20)
root.configure(bg='gray')

sub_label = tk.Label(root, text="Inscrição em tópicos", font=('Arial 20 bold'), padx=10, pady=10, background='gray')
sub_label.pack()

button1 = tk.Button(root, text="Sub topico luminosidade", command=button_luminosidade_callback, activeforeground='red')
button1.pack()

button2 = tk.Button(root, text="Sub topico led", command=button_led_callback, activeforeground='red')
button2.pack()

button3 = tk.Button(root, text="Sub topico cortina", command=button_cortina_callback, activeforeground='red')
button3.pack()

led_label = tk.Label(root, text="LED", font=('Arial 20 bold'), padx=10, pady=10, background='gray')
led_label.pack()

ligar_led = tk.Button(root, text="Ligar", command=ligar_led_callback, activeforeground='red')
ligar_led.pack()

desligar_led = tk.Button(root, text="Desligar", command=desligar_led_callback, activeforeground='red')
desligar_led.pack()

cortina_label = tk.Label(root, text="Cortina", font=('Arial 20 bold'), padx=10, pady=10, background='gray')
cortina_label.pack()

abrir_cortina = tk.Button(root, text="Abrir", command=abrir_cortina_callback, activeforeground='red')
abrir_cortina.pack()

fechar_cortina = tk.Button(root, text="Fechar", command=fechar_cortina_callback, activeforeground='red')
fechar_cortina.pack()

resultado_text = tk.Text(root, height=10, width=40)
resultado_text.pack()

scrollbar = Scrollbar(root, command=resultado_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
resultado_text.config(yscrollcommand=scrollbar.set)

root.mainloop()


