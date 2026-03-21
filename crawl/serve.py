"""Simple HTTP server to serve the UI and CSV files."""
import http.server
import webbrowser
import threading

PORT = 8888

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass  # silence request logs

def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")

print(f"🚀  Serving at http://localhost:{PORT}")
print(f"    Press Ctrl+C to stop\n")
threading.Timer(0.8, open_browser).start()
http.server.HTTPServer(("", PORT), Handler).serve_forever()
