# server.py
import asyncio
import websockets
import json
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading
from autocomplete import get_suggestion

PORT = 8000
WS_PORT = 8765
chat_history = []

clients = set()

async def handle_ws(websocket):
    clients.add(websocket)
    try:
        async for msg in websocket:
            data = json.loads(msg)
            if data["type"] == "message":
                chat_history.append((data["sender"], data["text"]))
                payload = json.dumps({"type": "message", "sender": data["sender"], "text": data["text"]})
                await asyncio.gather(*[client.send(payload) for client in clients])
            elif data["type"] == "suggest":
                prompt = "You are a helpful assistant. You are given a conversation history. You are supposed to keep the conversation alive. Conversation history:"

                # Build full prompt from history
                print("\n Suggestion Request From:", websocket.remote_address)

                for sender, text in chat_history:
                    prompt += f"{text}\n"
                prompt += f"You: {data['text']}"
                
                print("Full Prompt:\n", prompt)

                suggestion = get_suggestion(prompt)
                print("Generated Suggestion:", suggestion)

                await websocket.send(json.dumps({
                    "type": "suggestion",
                    "text": suggestion
                }))

    finally:
        clients.remove(websocket)

def serve_static():
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=".", **kwargs)

        def translate_path(self, path):
            # Remove any query parameters
            path = path.split('?',1)[0]
            path = path.split('#',1)[0]
            

            if path == "/":
                path = "/static/index.html"
            elif path == "/main.js":
                path = "/static/main.js"
            
            return SimpleHTTPRequestHandler.translate_path(self, path)

    with TCPServer(("", PORT), Handler) as httpd:
        print(f"[HTTP] Serving static files at http://localhost:{PORT}")
        httpd.serve_forever()

async def run_ws_server():
    print(f"[WebSocket] Running on ws://localhost:{WS_PORT}")
    async with websockets.serve(handle_ws, "0.0.0.0", WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    threading.Thread(target=serve_static, daemon=True).start()
    asyncio.run(run_ws_server())
