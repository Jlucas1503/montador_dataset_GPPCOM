import re
import pandas as pd
import config


def carregar_especies():
    """Lê o arquivo CSV no disco local e aplica filtros de categorias/limite."""
    if not config.CSV_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo CSV não encontrado em: {config.CSV_PATH.resolve()}"
        )

    df = pd.read_csv(config.CSV_PATH, encoding="utf-8-sig")

    if (
        config.CATEGORIAS
        and config.COL_CATEGORIA
        and config.COL_CATEGORIA in df.columns
    ):
        df = df[df[config.COL_CATEGORIA].isin(config.CATEGORIAS)]
    if config.LIMITE_ESPECIES:
        df = df.head(config.LIMITE_ESPECIES)

    return df.reset_index(drop=True)


def limpar_nome(texto):
    """Normaliza o nome científico e identifica se a consulta é genérica ou específica."""
    t = re.sub(r"\([^)]*\)", " ", str(texto)).strip()
    tokens = t.split()
    if not tokens:
        return None, None
    partes = [tokens[0]]
    for tok in tokens[1:]:
        if re.match(r"^spp?\.", tok) or tok.lower() in ("sp", "spp"):
            break
        if tok.lower() in ("cf.", "cf", "aff.", "aff"):
            continue
        if re.fullmatch(r"[a-z][a-z\-]+", tok) and len(partes) < 3:
            partes.append(tok)
        else:
            break
    rank = "genus" if len(partes) == 1 else None
    return " ".join(partes), rank