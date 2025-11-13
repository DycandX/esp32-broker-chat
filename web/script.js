const urlParams = new URLSearchParams(window.location.search);
const topic = urlParams.get("topic") || "chat/general";
document.getElementById("chat-title").textContent = topic;

const clientId = "WebUser_" + Math.floor(Math.random() * 1000);
const broker = "wss://broker.hivemq.com:8884/mqtt";
const client = mqtt.connect(broker);

client.on("connect", () => {
  console.log("✅ Connected to broker");
  client.subscribe(topic);
});

client.on("message", (t, msg) => {
  try {
    const data = JSON.parse(msg.toString());
    displayMessage(data.sender, data.text, data.status);
  } catch {
    console.log("⚠️ Non-JSON message:", msg.toString());
  }
});

function sendMessage() {
  const text = document.getElementById("msg").value.trim();
  if (!text) return;

  const message = {
    sender: clientId,
    text,
    status: "✓",
  };
  client.publish(topic, JSON.stringify(message));
  displayMessage(message.sender, message.text, message.status);
  document.getElementById("msg").value = "";
}

function displayMessage(sender, text, status) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message");
  msgDiv.innerHTML = `<span class="sender">${sender}:</span> ${text} <span>${status}</span>`;
  document.getElementById("messages").appendChild(msgDiv);
  msgDiv.scrollIntoView();
}

document.getElementById("send").addEventListener("click", sendMessage);
document.getElementById("msg").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
