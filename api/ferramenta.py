"""POST /api/ferramenta → todas as ferramentas além do gerador. Corpo: {"acao": "...", ...}."""
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
for _p in (_AQUI, os.path.dirname(_AQUI)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import json
from http.server import BaseHTTPRequestHandler

from _comum import responder

LIMITE_CORPO = 4_400_000


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            tam = int(self.headers.get("Content-Length") or 0)
            if tam > LIMITE_CORPO:
                return responder(self, 413, {"erro": "Arquivo grande demais para enviar (máx. ~3 MB)."})
            corpo = json.loads(self.rfile.read(tam) or b"{}")
            from servico.ferramentas import ErroUsuario, executar
            try:
                resp = executar(corpo)
            except ErroUsuario as e:
                return responder(self, 400, {"erro": str(e)})
        except json.JSONDecodeError:
            return responder(self, 400, {"erro": "Requisição inválida."})
        except Exception:
            return responder(self, 500, {"erro": "Não foi possível concluir a operação. Tente novamente."})
        responder(self, 200, resp)
