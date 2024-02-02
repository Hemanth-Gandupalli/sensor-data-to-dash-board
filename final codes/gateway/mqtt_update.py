from paho.mqtt.client import Client
import json
from datetime import datetime
from mail2 import mail2
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MqttConnect:
    def __init__(self):
        self.topic = []
        self._connected = False
        self._client = Client("MQTT")
        self._mqttBroker = "4.240.114.7"
        self._port = 1883
        self._username = "BarifloLabs"
        self._password = "Bfl@123"
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.on_log = self.log_message
        self._client.on_disconnect = self.on_disconnect
        self._client.connect_fail_callback = self.connect_fail_callback


    def on_connect(self, client, userdata, flags, rc):
        print(f"Connection result: {rc}")
        if rc == 0:
            print("Client Is Connected")
            self._connected = True
            for t in self.topic:
                client.subscribe(t)
        else:
            print("Connection Failed")

    def on_disconnect(self, userdata, flags, rc=0):
        print("Disconnected " + str(rc))
        self._connected = False

    def connect_fail_callback(self, userdata, flags, rc):
        print("Connection failed:", rc)
        self._connected = False

    def log_message(self, client, userdata, level, buf):
        try:
            print("log: " + buf)
        except Exception as e:
            print("Error" + str(e))

    def on_message(self, client, userdata, message):
        print("Received message: " + str(message.payload.decode("utf-8")))

    def connect_to_broker(self):
        try:
            self._client.username_pw_set(self._username, self._password)
            self._client.connect(self._mqttBroker, port=self._port)
            self._client.loop_start()
        except Exception as e:
            print(f"Error during connection: {e}")

    def data_publish(self, publish_data):
        if not self._connected:
            print("Not connected to the broker.")
            return
        publish_topic = publish_data["deviceId"]
        publish_data = json.dumps(publish_data)
        self._client.publish(publish_topic + "/data", publish_data)
        print(f"Just published {str(publish_data)} to {publish_topic}")
    
    def on_sub_message(self , client, userdata, message):
        global status
        status = None
        data = json.loads(message.payload.decode('utf-8'))
        status = data[0]["status"]
        print(f"Received message: {data}")
        print(f"status val :---{status}")
        with open("status.txt",'w') as f:
            f.write(str(status))
        self.mail2()
                    
    
    def open_file(self , file_name):
        if file_name.lower().endswith(".json"):
            with open(file_name) as json_file:
                data = json.load(json_file)
            return data
        
    def mail2(self):
        #time.sleep(20)
        try:
            with open("status.txt",'r') as f:
                status = f.read()
            s = status
            print(s)
            email_user = "care.bariflolabs@gmail.com"
            email_password = "ifln keco pdbc hqts"
            # email_send = "data.bariflolabs@gmail.com"
            email_send = "gandupallihemanth86@gmail.com"
            #email_send = "g"
            subject = "IWMS Status"

            msg = MIMEMultipart()
            msg["From"] = email_user
            msg["To"] = email_send
            msg["Subject"] = subject
            if  s == "True":
                with open('data.json', 'r') as file:
                    data = json.load(file)
                sensor1 = round(data["sensor1"],2)
                sensor2 = round(data["sensor2"],2)
                sensor3 = round(data["sensor3"],2) 
                sensor4 = round(data["sensor4"],2)
                x = round(data["x"],2)
                y = round(data["y"],2)
                z = round(data["z"],2)
                print("t")
                #body = f"GW_Status:ON  Aeration:On  CompCurrVal:{current1} Amp  AerationCurrVal:{current2} Amp"
                body = f"GW_Status:ON  Aeration:On  sensor1 :{sensor1} Amp\nsensor2 :{sensor2} Amp\nsensor3 :{sensor3} Amp\nsensor4 :{sensor4} Amp\nX :{x} Amp\nY :{y} Amp\nZ :{z} Amp"
            else:
                print("f")
                body = "GW_status:ON Aeration Device :OFF"


            msg.attach(MIMEText(body,"plain"))

            text = msg.as_string()
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login(email_user,email_password)


            server.sendmail(email_user,email_send,text)
            server.quit()
        except Exception as e:
            print(e)
    
    