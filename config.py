from pathlib import Path

# Caminhos de Arquivos e Diretorios
BASE_DIR = Path(__file__).resolve().parent ### PASTA ATUAL DO PROJETO
CSV_PATH = BASE_DIR / "fauna_parque_das_dunas_reduzido_v2.csv" ## Substitua pelo caminho do seu arquivo CSV
PASTA_SAIDA_DIR = BASE_DIR / "imagens_dataset"

# Nomes das Colunas no CSV
COL_ESPECIE = "Espécie"
COL_CATEGORIA = "Categoria"  # Defina como None se não houver categorias no CSV

# Filtros e Limites
CATEGORIAS = ["Mamíferos"]  # Exemplo: ["Aves"] ou None para todas
LIMITE_ESPECIES = None  # None para processar todas do CSV

# Configurações do iNaturalist
IMAGENS_POR_ESPECIE = 350
TAMANHO = "large"  # square | small | medium | large | original
LICENCAS = "cc0,cc-by,cc-by-nc,cc-by-sa,cc-by-nc-sa"
SO_GRAU_PESQUISA = True
PLACE_ID = None

# Controle de Cadência
PAUSA_INATURALIST = 0.4
PAUSA_DOWNLOAD = 0.05

API_INAT = "https://api.inaturalist.org/v1"
HEADERS_INAT = {"User-Agent": "fauna-dunas-natal/0.3 (projeto academico local)"}