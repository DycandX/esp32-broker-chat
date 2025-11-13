from mqtt_chat import ChatClient

# Ganti sesuai koneksi WiFi dan broker kamu
SSID = "S24 FE"
PASSWORD = "beliminum1"
BROKER = "broker.hivemq.com"
CLIENT_ID = "ESP32_1"

chat = ChatClient(SSID, PASSWORD, BROKER, CLIENT_ID)
chat.loop_forever()

