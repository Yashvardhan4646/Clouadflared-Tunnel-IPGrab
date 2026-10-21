
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from pathlib import Path
import json

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        try:
            html = Path("index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)
        except FileNotFoundError:
            self.send_error(404, "index.html not found")

    def do_POST(self):
        if self.path != "/record":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))

        if length > 4096:
            self.send_error(413, "Payload too large")
            return

        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "Invalid JSON")
            return

        ip = self.headers.get("CF-Connecting-IP", self.client_address[0])
        battery_raw = data.get("battery", "Unavailable")
        battery = f"{battery_raw}%" if battery_raw != "Unavailable" else "Unavailable"
        charging = data.get("charging", "Unavailable")

        with open("visits.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.now().isoformat()} | "
                f"IP: {ip} | "
                f"Battery: {battery} | "
                f"Charging: {charging}\n"
            )

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Visit recorded")

    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - {format % args}")

if __name__ == "__main__":
    port = 6767
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[*] Server listening on http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        server.server_close()

