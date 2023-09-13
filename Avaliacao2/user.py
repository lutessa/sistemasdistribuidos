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
        info = client.publish("topic/estado_led","LIGADO")
        print("publish 'LIGADO' connection status code is", info.rc)
        print("publish 'LIGADO' message id is", info.mid)
        ## TODO: print result code
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
root.geometry("600x400")
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

root.mainloop()

client.on_message = on_message

client.loop_forever()
