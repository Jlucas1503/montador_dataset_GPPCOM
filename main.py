import time
import config
from downloader import listar_existentes, obter_pasta_destino, salvar_fotos
from inaturalist import buscar_fotos, buscar_taxon
from taxonomy import carregar_especies, limpar_nome


def processar():
    df = carregar_especies()
    nao_encontradas, sem_fotos, concluidas = [], [], 0

    print(
        f"Iniciando download do dataset. Destino: {config.PASTA_SAIDA_DIR.resolve()}\n"
    )

    for i, linha in df.iterrows():
        original = linha[config.COL_ESPECIE]
        categoria = (
            linha[config.COL_CATEGORIA]
            if (config.COL_CATEGORIA and config.COL_CATEGORIA in linha)
            else None
        )
        nome, rank = limpar_nome(original)

        if not nome:
            continue

        print(f"[{i+1}/{len(df)}] {nome}", end=" ... ")

        pasta_destino, seguro = obter_pasta_destino(categoria, nome)
        existentes = listar_existentes(pasta_destino)

        if len(existentes) >= config.IMAGENS_POR_ESPECIE:
            print("já possui fotos suficientes no disco, pulando.")
            concluidas += 1
            continue

        taxon = buscar_taxon(nome, rank)
        time.sleep(config.PAUSA_INATURALIST)

        if not taxon:
            print("táxon NÃO encontrado")
            nao_encontradas.append(original)
            continue

        fotos = buscar_fotos(taxon["id"], config.IMAGENS_POR_ESPECIE)
        if not fotos:
            print("sem fotos disponíveis com licença aberta")
            sem_fotos.append(nome)
            continue

        n = salvar_fotos(fotos, pasta_destino, seguro, existentes)
        print(f"{n} imagem(ns) salvas no disco")
        concluidas += 1

    print("\n===== RESUMO DA EXECUÇÃO =====")
    print(f"Concluídas com sucesso: {concluidas}/{len(df)}")
    print(f"Táxon não encontrado ({len(nao_encontradas)}): {nao_encontradas}")
    print(f"Sem fotos ({len(sem_fotos)}): {sem_fotos}")


if __name__ == "__main__":
    processar()