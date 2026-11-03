import argparse
import time
import config
from downloader import listar_existentes, obter_pasta_destino, salvar_fotos
from inaturalist import buscar_fotos, buscar_taxon
from taxonomy import carregar_especies, limpar_nome


def inteiro_positivo(valor):
    """Converte um argumento da CLI em um inteiro maior que zero."""
    try:
        numero = int(valor)
    except ValueError as erro:
        raise argparse.ArgumentTypeError("informe um número inteiro") from erro
    if numero <= 0:
        raise argparse.ArgumentTypeError("informe um número maior que zero")
    return numero


def criar_parser():
    """Cria o parser dos argumentos aceitos pela linha de comando."""
    parser = argparse.ArgumentParser(
        description="Baixa imagens de espécies usando a API do iNaturalist."
    )
    parser.add_argument(
        "--especie",
        help="nome científico a processar diretamente, sem ler o CSV",
    )
    parser.add_argument(
        "--quantidade",
        type=inteiro_positivo,
        help=(
            "quantidade de imagens por espécie; por padrão, usa "
            "IMAGENS_POR_ESPECIE do config.py"
        ),
    )
    return parser


def selecionar_registros(especie=None):
    """Seleciona uma espécie da CLI ou carrega os registros configurados no CSV."""
    if especie is not None:
        nome = especie.strip()
        if not nome:
            raise ValueError("O nome da espécie não pode ficar vazio.")
        return [{config.COL_ESPECIE: nome}]
    return carregar_especies().to_dict(orient="records")


def processar(especie=None, quantidade=None):
    registros = selecionar_registros(especie)
    quantidade_imagens = (
        quantidade if quantidade is not None else config.IMAGENS_POR_ESPECIE
    )
    nao_encontradas, sem_fotos, concluidas = [], [], 0

    print(
        f"Iniciando download do dataset. Destino: {config.PASTA_SAIDA_DIR.resolve()}\n"
    )

    for i, linha in enumerate(registros):
        original = linha[config.COL_ESPECIE]
        categoria = (
            linha.get(config.COL_CATEGORIA)
            if config.COL_CATEGORIA
            else None
        )
        nome, rank = limpar_nome(original)
        if not nome:
            continue

        print(f"[{i+1}/{len(registros)}] {nome}", end=" ... ")

        pasta_destino, seguro = obter_pasta_destino(categoria, nome)
        existentes = listar_existentes(pasta_destino)

        if len(existentes) >= quantidade_imagens:
            print("já possui fotos suficientes no disco, pulando")
            concluidas += 1
            continue

        taxon = buscar_taxon(nome, rank)
        time.sleep(config.PAUSA_INATURALIST)

        if not taxon:
            print("táxon NÃO encontrado")
            nao_encontradas.append(original)
            continue

        fotos = buscar_fotos(taxon["id"], quantidade_imagens)
        if not fotos:
            print("sem fotos disponíveis com licença aberta")
            sem_fotos.append(nome)
            continue

        n = salvar_fotos(fotos, pasta_destino, seguro, existentes)
        print(f"{n} imagem(ns) salvas no disco")
        concluidas += 1

    print("\n===== RESUMO DA EXECUÇÃO =====")
    print(f"Concluídas: {concluidas}/{len(registros)}")
    print(f"Táxon não encontrado ({len(nao_encontradas)}): {nao_encontradas}")
    print(f"Sem fotos ({len(sem_fotos)}): {sem_fotos}")


if __name__ == "__main__":
    argumentos = criar_parser().parse_args()
    processar(especie=argumentos.especie, quantidade=argumentos.quantidade)
