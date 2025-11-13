import network
from umqtt.simple import MQTTClient
import ujson
import time
import os


class ChatClient:
    def __init__(self, ssid, password, broker, client_id):
        self.ssid = ssid
        self.password = password
        self.broker = broker
        self.client_id = client_id
        self.topics = ["chat/general", "chat/esp32", "chat/test"]
        self.history_file = "chat_history.json"
        self.sent_cache = set()  # mencegah duplikat pesan

        self.wifi_connect()
        self.client = MQTTClient(client_id, broker, keepalive=60)
        self.client.set_callback(self.on_message)
        self.load_history()
        self.connect_mqtt()

    # ---------- WIFI ----------
    def wifi_connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)
        print("Menghubungkan ke WiFi...")
        while not wlan.isconnected():
            time.sleep(0.5)
        print("✅ WiFi Connected:", wlan.ifconfig())

    # ---------- MQTT ----------
    def connect_mqtt(self):
        try:
            self.client.connect()
            for t in self.topics:
                self.client.subscribe(t.encode())
            print("📡 Subscribed to:", self.topics)
        except Exception as e:
            print("⚠️ Gagal connect MQTT:", e)

    def on_message(self, topic, msg):
        try:
            data = ujson.loads(msg)
            sender = data.get("sender", "")
            text = data.get("text", "")
            status = data.get("status", "")

            print(f"[{topic.decode()}] {sender}: {text} ({status})")

            # Hanya balas jika ada perintah khusus
            if sender != self.client_id and text.startswith("!esp"):
                reply = f"Perintah '{text}' diterima oleh ESP32"
                resp = {
                    "sender": self.client_id,
                    "text": reply,
                    "status": "✓"
                }
                self.client.publish(topic, ujson.dumps(resp))
                self.save_message(topic.decode(), resp)

            # Simpan semua pesan masuk (kecuali pesan duplikat)
            msg_id = f"{sender}:{text}"
            if msg_id not in self.sent_cache:
                self.save_message(topic.decode(), data)
                self.sent_cache.add(msg_id)

        except Exception as e:
            print("⚠️ Error parsing message:", e)

    # ---------- SEND ----------
    def send_message(self, topic, text):
        message = {"sender": self.client_id, "text": text, "status": "✓"}
        msg_json = ujson.dumps(message)
        self.client.publish(topic.encode(), msg_json.encode('utf-8'))
        self.save_message(topic, message)

    # ---------- HISTORY ----------
    def save_message(self, topic, message):
        if topic not in self.history:
            self.history[topic] = []
        self.history[topic].append(message)
        try:
            with open(self.history_file, "w") as f:
                ujson.dump(self.history, f)
        except Exception as e:
            print("⚠️ Gagal simpan:", e)

    def load_history(self):
        if self.history_file in os.listdir():
            try:
                with open(self.history_file, "r") as f:
                    self.history = ujson.load(f)
            except:
                self.history = {}
        else:
            self.history = {}

    # ---------- LOOP ----------
    def loop_forever(self):
        while True:
            try:
                self.client.check_msg()
                time.sleep(0.2)
            except OSError:
                print("⚠️ Terputus, mencoba reconnect...")
                time.sleep(3)
                try:
                    self.client = MQTTClient(self.client_id, self.broker, keepalive=60)
                    self.client.set_callback(self.on_message)
                    self.connect_mqtt()
                    print("✅ Reconnected sukses.")
                except Exception as err:
                    print("Gagal reconnect:", err)
                    time.sleep(5)

