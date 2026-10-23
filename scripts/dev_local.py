"""Servidor local que imita a Vercel (estático em public/ + /api/*) para testes."""
import importlib.util, os, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [R, os.path.join(R, "api")]
def carregar(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(R, "api", n + ".py")); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.handler
H = {"/api/gerar": carregar("gerar"), "/api/setores": carregar("setores")}
class D(SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=os.path.join(R, "public"), **k)
    def _api(s, met):
        h = H.get(s.path.split("?")[0])
        if not h: return False
        getattr(h, "do_" + met)(s); return True
    def do_GET(s):
        if not s._api("GET"): super().do_GET()
    def do_POST(s):
        if not s._api("POST"): s.send_error(404)
HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8765), D).serve_forever()
