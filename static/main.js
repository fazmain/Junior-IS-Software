const ws = new WebSocket("ws://" + location.hostname + ":8765");
const chatDiv = document.getElementById("chat");
const msgBox = document.getElementById("msg");
const ghostBox = document.getElementById("ghost");
const sender = prompt("Enter your name (e.g., You or Friend):") || "User";

let lastSuggestion = "";
let debounceTimer;

// Helper function to create message elements
function createMessageElement(sender, text) {
  const div = document.createElement("div");
  div.className = "message";
  div.innerHTML = `<b>${sender}:</b> ${text}`;
  return div;
}

// Helper function to show/hide suggestion with animation
function showSuggestion(text) {
  ghostBox.textContent = text;
  ghostBox.classList.add("visible");
}

function hideSuggestion() {
  ghostBox.classList.remove("visible");
  ghostBox.textContent = "";
}

// Add loading animation to send button
function setLoadingState(loading) {
  const sendBtn = document.getElementById("sendBtn");
  if (loading) {
    const originalText = sendBtn.innerHTML;
    sendBtn.setAttribute("data-original-text", originalText);
    sendBtn.innerHTML = `
      <svg class="loading" viewBox="0 0 24 24" style="width: 20px; height: 20px; animation: spin 1s linear infinite;">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" stroke-dasharray="31.4 31.4">
          <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
        </circle>
      </svg>
    `;
  } else {
    const originalText = sendBtn.getAttribute("data-original-text");
    sendBtn.innerHTML = originalText;
  }
}

msgBox.addEventListener("input", () => {
  const text = msgBox.value;
  hideSuggestion();
  lastSuggestion = "";

  clearTimeout(debounceTimer);

  if (sender === "You") {
    debounceTimer = setTimeout(() => {
      if (text.trim()) {
        ws.send(JSON.stringify({ type: "suggest", text }));
      }
    }, 1000); // 1 second delay
  }
});

msgBox.addEventListener("keydown", function (e) {
  if (e.key === "Tab" && lastSuggestion) {
    e.preventDefault();
    msgBox.value += lastSuggestion;
    hideSuggestion();
    lastSuggestion = "";
  } else if (e.key === "Enter") {
    e.preventDefault();
    send();
  }
});

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "message") {
    const messageElement = createMessageElement(data.sender, data.text);
    chatDiv.appendChild(messageElement);
    chatDiv.scrollTop = chatDiv.scrollHeight;
  } else if (data.type === "suggestion" && sender === "You") {
    const typed = msgBox.value;
    const full = typed + data.text.trim();
    if (full.startsWith(typed)) {
      lastSuggestion = full.slice(typed.length);
      showSuggestion(`${lastSuggestion}`);
    }
  }
};

function send() {
  const text = msgBox.value.trim();
  if (!text) return;

  setLoadingState(true);

  ws.send(JSON.stringify({ type: "message", sender: sender, text: text }));

  setTimeout(() => {
    setLoadingState(false);
    msgBox.value = "";
    hideSuggestion();
    lastSuggestion = "";
  }, 500);
}

// Add keyframe animation for loading spinner
const style = document.createElement("style");
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);
