"""GET /api/setores → lista dos setores disponíveis."""
from http.server import BaseHTTPRequestHandler

from _comum import responder


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from servico.pacote import listar_setores
        responder(self, 200, {"setores": listar_setores()},
                  cache="public, s-maxage=86400, stale-while-revalidate=604800")
