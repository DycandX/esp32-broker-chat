import network
from umqtt.simple import MQTTClient
import ujson
import time
import os


class ChatClient:
    def __init__(self, ssid, password, broker, client_id):
        self.wifi_connect(ssid, password)
        self.broker = broker
        self.client_id = client_id
        self.topics = ["chat/general", "chat/esp32", "chat/test"]
        self.history_file = "chat_history.json"
        self.client = MQTTClient(client_id, broker, keepalive=60)
        self.client.set_callback(self.on_message)
        self.load_history()
        self.connect_mqtt()
        self.last_msg = None  # hindari kirim ulang pesan sama

    def wifi_connect(self, ssid, password):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        print("Menghubungkan ke WiFi...")
        while not wlan.isconnected():
            time.sleep(0.5)
        print("WiFi Connected:", wlan.ifconfig())

    def connect_mqtt(self):
        try:
            self.client.connect()
            for t in self.topics:
                self.client.subscribe(t.encode())
            print("Subscribed to topics:", self.topics)
        except Exception as e:
            print("Gagal connect MQTT:", e)

    def on_message(self, topic, msg):
        topic = topic.decode()
        try:
            message = ujson.loads(msg)
            sender = message.get("sender", "")
            text = message.get("text", "")
            if sender == self.client_id:
                return  # abaikan pesan sendiri
            print(f"[{topic}] {sender}: {text}")
            self.save_message(topic, message)
        except Exception:
            print(f"[{topic}] Pesan bukan JSON valid: {msg}")

    def send_message(self, topic, text):
        message = {"sender": self.client_id, "text": text, "status": "✓"}
        msg_json = ujson.dumps(message)
        if msg_json != self.last_msg:
            print("Kirim pesan:", msg_json)
            self.client.publish(topic.encode(), msg_json.encode('utf-8'))
            self.save_message(topic, message)
            self.last_msg = msg_json

    def save_message(self, topic, message):
        if topic not in self.history:
            self.history[topic] = []
        self.history[topic].append(message)
        try:
            with open(self.history_file, "w") as f:
                ujson.dump(self.history, f)
        except Exception as e:
            print("Gagal simpan:", e)

    def load_history(self):
        if self.history_file in os.listdir():
            try:
                with open(self.history_file, "r") as f:
                    self.history = ujson.load(f)
            except:
                self.history = {}
        else:
            self.history = {}

    def loop_forever(self):
        while True:
            try:
                self.client.check_msg()
                time.sleep(0.2)  # delay agar tidak diblok broker
            except OSError as e:
                print("⚠️  Terputus, mencoba reconnect...")
                try:
                    self.client.disconnect()
                except:
                    pass
                time.sleep(3)
                try:
                    self.connect_mqtt()
                except Exception as err:
                    print("Gagal reconnect:", err)
                    time.sleep(5)
