"""
POST /api/gerar → gera o pacote do setor.

Corpo JSON: {setor, linhas, inicio, fim, mes_fiscal, anomalia, deriva, idioma}
Resposta: {resumo, zip_nome, zip_base64} (zip pequeno) ou {resumo, zip_nome, zip_url}
(zip grande: enviado ao Supabase Storage; exige SUPABASE_URL e SUPABASE_SERVICE_KEY).
"""
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
for _p in (_AQUI, os.path.dirname(_AQUI)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import base64
import json
import os
import urllib.request
import uuid
from datetime import date
from http.server import BaseHTTPRequestHandler

from _comum import responder

LIMITE_INLINE = 3_000_000  # bytes; base64 (+33%) precisa caber em ~4,5 MB da resposta


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            tam = int(self.headers.get("Content-Length") or 0)
            if tam > 10_000:
                return responder(self, 413, {"erro": "Requisição grande demais."})
            p = json.loads(self.rfile.read(tam) or b"{}")
            from servico.pacote import gerar_pacote
            zip_bytes, resumo = gerar_pacote(
                str(p.get("setor", "")), int(p.get("linhas", 0)),
                date.fromisoformat(p["inicio"]), date.fromisoformat(p["fim"]),
                mes_fiscal=int(p.get("mes_fiscal", 1)),
                anomalia=bool(p.get("anomalia")), drift=bool(p.get("deriva")),
                lang=str(p.get("idioma", "pt")),
                seed=int(p["seed"]) if p.get("seed") is not None else None)
        except (ValueError, KeyError, TypeError) as e:
            return responder(self, 400, {"erro": str(e) or "Parâmetros inválidos."})
        except Exception:
            return responder(self, 500, {"erro": "Falha ao gerar a base. Tente um volume menor."})

        nome = "Base_BI_" + resumo["setor"].replace(" ", "_").replace("/", "_") + ".zip"
        corpo = {"resumo": resumo, "zip_nome": nome}
        if len(zip_bytes) <= LIMITE_INLINE:
            corpo["zip_base64"] = base64.b64encode(zip_bytes).decode()
        else:
            try:
                from servico.armazenamento import enviar
                url = enviar(nome, zip_bytes)
            except Exception:
                url = None
            if not url:
                return responder(self, 413, {"erro": "O pacote ficou grande demais para baixar direto. "
                                                      "Reduza o volume de linhas."})
            corpo["zip_url"] = url
        responder(self, 200, corpo)
