import socket
import threading
import time
import webview
import uvicorn
from backend.app import app

def get_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def run_server(port):
    """Run the FastAPI server."""
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    port = get_free_port()
    url = f"http://127.0.0.1:{port}"
    
    print(f"[*] Starting Kundli Generator on port {port}...")
    
    # Start server in a background thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    print(f"[*] Opening desktop window: {url}")
    
    # Create a desktop window
    webview.create_window(
        "Kundli Generator",
        url,
        width=1200,
        height=800,
        min_size=(800, 600)
    )
    webview.start()
