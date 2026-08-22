#!/usr/bin/env python3
"""Docker API reverse proxy — exposes Docker daemon API on Tailscale IP.
Properly proxies HTTP requests (including chunked encoding) from
Tailscale IP:2375 to localhost:2375.
Runs as a daemon via pythonw.exe — no console window.
"""
import http.server
import http.client
import urllib.request
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_FILE = BASE / "10_Skills_Library/05_Operations/logs/docker_proxy.log"

def log(msg: str) -> None:
    try:
        now = datetime.now(timezone.utc).isoformat()
        line = f"[{now}] {msg}"
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass

class DockerProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy()
    
    def do_POST(self):
        self._proxy()
    
    def do_DELETE(self):
        self._proxy()
    
    def do_PUT(self):
        self._proxy()
    
    def do_PATCH(self):
        self._proxy()
    
    def do_HEAD(self):
        self._proxy()
    
    def _proxy(self):
        """Forward request to Docker daemon on localhost:2375."""
        try:
            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Connect to Docker daemon
            conn = http.client.HTTPConnection("127.0.0.1", 2375, timeout=30)
            
            # Forward headers (filter hop-by-hop)
            headers = {}
            for key, val in self.headers.items():
                if key.lower() not in ('host', 'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization'):
                    headers[key] = val
            headers['Host'] = 'localhost:2375'
            headers['Connection'] = 'close'
            
            # Forward request
            method = self.command
            conn.request(method, self.path, body=body, headers=headers)
            response = conn.getresponse()
            
            # Send response back to client
            self.send_response(response.status, response.reason)
            
            # Forward response headers
            for key, val in response.getheaders():
                if key.lower() not in ('connection', 'transfer-encoding', 'keep-alive'):
                    self.send_header(key, val)
            self.send_header('Connection', 'close')
            self.end_headers()
            
            # Forward response body
            data = response.read()
            self.wfile.write(data)
            
            conn.close()
        except Exception as e:
            log(f"Proxy error: {e}")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Proxy error: {e}".encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def get_tailscale_ip() -> str:
    """Get PINKCADY's Tailscale IP."""
    try:
        import subprocess
        r = subprocess.run(
            ["tailscale", "status"],
            capture_output=True, text=True, timeout=5,
            creationflags=0x08000000
        )
        for line in r.stdout.split("\n"):
            if "pinkcady" in line.lower():
                return line.split()[0]
    except Exception:
        pass
    return "100.106.235.103"

class ThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True

def main():
    ts_ip = get_tailscale_ip()
    log(f"DOCKER_PROXY_STARTED — reverse proxy {ts_ip}:2375 -> 127.0.0.1:2375")
    
    server = ThreadingHTTPServer((ts_ip, 2375), DockerProxyHandler)
    log(f"Listening on {ts_ip}:2375")
    server.serve_forever()

if __name__ == "__main__":
    main()
