"""Loopback-only research studio. Never sends email."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit
from contact_core import ContactError, extract_contacts, drafts, draft_archive, csv_export

WEB = Path(__file__).parent / "web"
ASSETS = {"/favicon.svg": ("favicon.svg", "image/svg+xml"), "/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"), "/style.css": ("style.css", "text/css"), "/sample.json": ("sample.json", "application/json")}

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, content, kind="application/json", download=None):
        if isinstance(content, dict):
            content = json.dumps(content).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(content)

    def local_request(self):
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        return self.headers.get("Host") in expected and (not origin or origin in {"http://" + h for h in expected})

    def do_GET(self):
        if not self.local_request():
            self.reply(403, {"error": "Use this studio from its localhost address."})
            return
        asset = ASSETS.get(urlsplit(self.path).path)
        if not asset:
            self.reply(404, {"error": "Not found"})
            return
        self.reply(200, (WEB / asset[0]).read_bytes(), asset[1])

    def do_POST(self):
        if not self.local_request() or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self.reply(403, {"error": "Use the local studio to submit JSON."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1_500_000:
                raise ContactError("This request is too large or empty.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ContactError("Expected a JSON object.")
            if self.path == "/api/extract":
                self.reply(200, {"contacts": extract_contacts(data.get("text"), data.get("url"), data.get("organization", ""))})
            elif self.path == "/api/preview":
                self.reply(200, {"drafts": drafts(data.get("contacts"), data.get("subject"), data.get("body"))})
            elif self.path == "/api/export":
                self.reply(200, draft_archive(data.get("contacts"), data.get("subject"), data.get("body")), "application/zip", "research-drafts.zip")
            elif self.path == "/api/contacts":
                self.reply(200, csv_export(data.get("contacts")), "text/csv", "reviewed-contacts.csv")
            else:
                self.reply(404, {"error": "Not found"})
        except (ContactError, ValueError, TypeError, UnicodeError) as exc:
            self.reply(400, {"error": str(exc)})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Research studio: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
