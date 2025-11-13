from mqtt_chat import ChatClient

SSID = "S24 FE"
PASSWORD = "beliminum1"
BROKER = "broker.hivemq.com"
CLIENT_ID = "ESP32_Chat_A"

chat = ChatClient(SSID, PASSWORD, BROKER, CLIENT_ID)
chat.send_message("chat/general", "Halo dari ESP A!")
chat.loop_forever()
