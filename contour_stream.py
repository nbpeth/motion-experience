import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

CONTOUR_PATH = "/contours"


class _Channel:
    def __init__(self):
        self._condition = threading.Condition()
        self._value = None
        self._id = 0

    def publish(self, value):
        with self._condition:
            self._value = value
            self._id += 1
            self._condition.notify_all()

    def wait_next(self, last_id, timeout=1):
        with self._condition:
            self._condition.wait_for(lambda: self._id != last_id, timeout=timeout)
            return self._value, self._id


class ContourStreamer:
    def __init__(self, port=8001):
        self.port = port
        self._contours = _Channel()

    def publish_contours(self, payload):
        self._contours.publish(json.dumps(payload).encode())

    def start(self):
        streamer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if urlsplit(self.path).path != CONTOUR_PATH:
                    self.send_error(404)
                    return

                self.send_response(200)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                last_id = 0
                try:
                    while True:
                        data, new_id = streamer._contours.wait_next(last_id)
                        if new_id == last_id:
                            continue
                        last_id = new_id
                        self.wfile.write(b"data: ")
                        self.wfile.write(data)
                        self.wfile.write(b"\n\n")
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("", self.port), Handler)
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        
        print(f"Contour stream at http://localhost:{self.port}{CONTOUR_PATH}")
