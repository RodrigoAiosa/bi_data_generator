"""GET /api/setores → lista dos setores disponíveis."""
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
for _p in (_AQUI, os.path.dirname(_AQUI)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from http.server import BaseHTTPRequestHandler

from _comum import responder


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from servico.pacote import listar_setores
        responder(self, 200, {"setores": listar_setores()},
                  cache="public, s-maxage=86400, stale-while-revalidate=604800")
