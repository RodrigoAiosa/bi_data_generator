"""servico/armazenamento.py: envia arquivos grandes ao bucket privado 'pacotes' do Supabase Storage
e devolve uma URL assinada (1 h). Exige SUPABASE_URL e SUPABASE_SERVICE_KEY (só no servidor)."""
import json
import os
import urllib.request
import uuid


def enviar(nome: str, dados: bytes, mime: str = "application/zip") -> str | None:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    chave = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not chave:
        return None
    caminho = f"{uuid.uuid4().hex}/{nome}"
    cab = {"apikey": chave, "Authorization": f"Bearer {chave}"}
    urllib.request.urlopen(urllib.request.Request(
        f"{url}/storage/v1/object/pacotes/{caminho}", data=dados, method="POST",
        headers={**cab, "Content-Type": mime}), timeout=40).read()
    assinada = json.loads(urllib.request.urlopen(urllib.request.Request(
        f"{url}/storage/v1/object/sign/pacotes/{caminho}", method="POST",
        data=json.dumps({"expiresIn": 3600}).encode(),
        headers={**cab, "Content-Type": "application/json"}), timeout=15).read())["signedURL"]
    return f"{url}/storage/v1{assinada}"
