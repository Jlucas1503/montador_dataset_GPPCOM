import time
import requests
import config


def api_get_inat(endpoint, params):
    """Requisição HTTP genérica com nova tentativa automatizada."""
    for tentativa in range(4):
        try:
            r = requests.get(
                f"{config.API_INAT}/{endpoint}",
                params=params,
                headers=config.HEADERS_INAT,
                timeout=30,
            )
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(5 * (tentativa + 1))
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            time.sleep(3 * (tentativa + 1))
    return None


def buscar_taxon(nome, rank=None):
    """Busca e valida o ID do táxon no iNaturalist."""
    dados = api_get_inat("taxa", {"q": nome, "per_page": 15, "locale": "pt-BR"})
    if not dados:
        return None
    resultados = dados.get("results", [])
    if rank:
        resultados = [t for t in resultados if t.get("rank") == rank]
    alvo = nome.lower()
    exatos = [t for t in resultados if t.get("name", "").lower() == alvo]
    exatos.sort(key=lambda t: not t.get("is_active", True))
    if exatos:
        return exatos[0]
    sinonimos = [
        t for t in resultados if str(t.get("matched_term", "")).lower() == alvo
    ]
    return sinonimos[0] if sinonimos else None


def buscar_fotos(taxon_id, quantidade):
    """Busca URLs de fotos com paginação (ultrapassando o limite de 200/página da API)."""
    fotos = []
    pagina = 1
    por_pagina = 200

    while len(fotos) < quantidade:
        params = {
            "taxon_id": taxon_id,
            "photos": "true",
            "photo_license": config.LICENCAS,
            "order_by": "votes",
            "order": "desc",
            "per_page": por_pagina,
            "page": pagina,
        }
        if config.SO_GRAU_PESQUISA:
            params["quality_grade"] = "research"
        if config.PLACE_ID:
            params["place_id"] = config.PLACE_ID

        dados = api_get_inat("observations", params)
        resultados = (dados or {}).get("results", [])

        if not resultados:
            break

        for obs in resultados:
            for foto in obs.get("photos", [])[:1]:
                url = foto.get("url")
                if not url:
                    continue
                fotos.append(
                    {
                        "obs_id": obs["id"],
                        "url": url.replace("/square.", f"/{config.TAMANHO}."),
                        "licenca": foto.get("license_code") or "sem-licenca",
                    }
                )
                if len(fotos) >= quantidade:
                    break
            if len(fotos) >= quantidade:
                break

        pagina += 1
        time.sleep(config.PAUSA_INATURALIST)

    return fotos