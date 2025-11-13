const clientId = "WebUser_" + Math.floor(Math.random() * 1000);
const topic = "chat/general"; // bisa diganti sesuai kebutuhan
const chatName = "Istri";
document.getElementById("chatName").innerText = chatName;

// Koneksi MQTT
const client = mqtt.connect("wss://broker.hivemq.com:8884/mqtt");

client.on("connect", () => {
  client.subscribe(topic);
  console.log("Terhubung ke broker dan subscribe ke:", topic);
});

let messageHistory = []; // untuk menyimpan pesan dan status

function renderMessages() {
  const container = document.getElementById("messages");
  container.innerHTML = "";
  messageHistory.forEach((msg) => {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("msg", msg.isMe ? "me" : "other");
    msgDiv.id = msg.id;

    const time = new Date(msg.time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    const checkColor = msg.status === "✓✓" ? "checkmark read" : "checkmark";

    msgDiv.innerHTML = `
      <div>${msg.text}</div>
      <div class="timestamp">${time} <span class="${checkColor}">${
      msg.isMe ? msg.status : ""
    }</span></div>
    `;
    container.appendChild(msgDiv);
  });
  container.scrollTop = container.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("msg");
  const text = input.value.trim();
  if (!text) return;

  const message = {
    id: "msg_" + Date.now(),
    sender: clientId,
    text: text,
    time: new Date().toISOString(),
    status: "✓",
  };

  messageHistory.push({ ...message, isMe: true });
  renderMessages();

  client.publish(topic, JSON.stringify(message));
  input.value = "";
}

client.on("message", (t, payload) => {
  const msg = JSON.parse(payload.toString());

  // Jika pesan dari diri sendiri dan status berubah, update status tanpa duplikasi
  const existing = messageHistory.find((m) => m.id === msg.id);
  if (existing) {
    existing.status = msg.status;
  } else {
    const isMe = msg.sender === clientId;
    messageHistory.push({ ...msg, isMe });
  }

  renderMessages();

  // Jika bukan pesan kita sendiri, ubah status menjadi ✓✓ (sudah dibaca)
  if (msg.sender !== clientId && msg.status === "✓") {
    msg.status = "✓✓";
    client.publish(topic, JSON.stringify(msg));
  }
});

document.getElementById("sendBtn").onclick = sendMessage;
document.getElementById("msg").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
