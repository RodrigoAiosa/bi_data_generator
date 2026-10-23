"""Utilitários compartilhados das funções serverless (prefixo _ = não vira rota)."""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)


def responder(handler, status: int, corpo: dict, cache: str = "no-store") -> None:
    dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(dados)))
    handler.send_header("Cache-Control", cache)
    handler.end_headers()
    handler.wfile.write(dados)
