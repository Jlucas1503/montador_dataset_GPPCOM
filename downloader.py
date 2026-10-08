import re
import time
from pathlib import Path
import requests
import config


def obter_pasta_destino(categoria, nome):
    """Cria e retorna a estrutura de diretórios para a espécie."""
    seguro = re.sub(r"[^\w\-]+", "_", nome).strip("_")
    if config.COL_CATEGORIA and categoria:
        cat_segura = re.sub(r"[^\w\-]+", "_", str(categoria)).strip("_")
        pasta = config.PASTA_SAIDA_DIR / cat_segura / seguro
    else:
        pasta = config.PASTA_SAIDA_DIR / seguro

    pasta.mkdir(parents=True, exist_ok=True)
    return pasta, seguro


def listar_existentes(pasta):
    """Retorna os nomes dos arquivos já baixados na pasta da espécie."""
    if not pasta.exists():
        return set()
    return {f.name for f in pasta.glob("*") if f.is_file()}


def salvar_fotos(fotos, pasta_destino, nome_base, existentes):
    """Realiza o download e grava as imagens no disco."""
    salvas = len(existentes)

    for f in fotos:
        ext = Path(f["url"].split("?")[0]).suffix or ".jpg"
        nome_arq = f"{nome_base}_{f['obs_id']}_{f['licenca']}{ext}"

        if nome_arq in existentes:
            continue

        try:
            r = requests.get(f["url"], headers=config.HEADERS_INAT, timeout=30)
            if r.status_code == 200:
                caminho_arquivo = pasta_destino / nome_arq
                caminho_arquivo.write_bytes(r.content)
                existentes.add(nome_arq)
                salvas += 1
        except Exception as e:
            print(f"\n[Erro Download] Imagem {f['obs_id']}: {e}")

        time.sleep(config.PAUSA_DOWNLOAD)

    return salvas