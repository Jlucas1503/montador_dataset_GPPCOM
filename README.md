# GPPCOM Dataset — coletor de imagens de fauna

Este projeto cria um dataset de imagens de espécies da fauna usando observações públicas do [iNaturalist](https://www.inaturalist.org/). A lista de espécies é lida de um arquivo CSV, os nomes científicos são normalizados, os táxons correspondentes são localizados na API do iNaturalist e as imagens licenciadas são organizadas em pastas por categoria e espécie.

O CSV incluído atualmente contém 124 registros:

- 90 aves;
- 18 répteis;
- 13 mamíferos;
- 3 anfíbios.

## Como o projeto funciona

O fluxo principal é:

1. `main.py` inicia o processamento.
2. `taxonomy.py` lê o CSV, aplica os filtros configurados e limpa os nomes científicos.
3. `inaturalist.py` pesquisa o táxon e as observações com fotos na API do iNaturalist.
4. `downloader.py` cria as pastas e salva as imagens, evitando baixar novamente arquivos que já existem.
5. Ao final, o programa mostra quantas espécies foram concluídas, não encontradas ou não tinham fotos elegíveis.

## Estrutura do projeto

```text
GPPCOM_dataset/
├── config.py                              # caminhos, filtros e parâmetros
├── main.py                                # ponto de entrada e orquestração
├── taxonomy.py                            # leitura do CSV e limpeza dos nomes
├── inaturalist.py                         # integração com a API do iNaturalist
├── downloader.py                          # criação de pastas e download das imagens
├── requirements.txt                       # dependências Python
└── fauna_parque_das_dunas_reduzido_v2.csv # catálogo de espécies
```

A pasta `imagens_dataset/` é criada automaticamente na primeira execução, caso ainda não exista.

## Pré-requisitos

- Python 3.11 ou 3.12 recomendado;
- acesso à internet para consultar o iNaturalist e baixar as imagens;
- espaço em disco suficiente para a quantidade e o tamanho escolhidos.

> O projeto pode funcionar em outras versões do Python, mas as dependências devem oferecer suporte à versão instalada. O ambiente precisa ter, no mínimo, `pandas` e `requests`.

## Instalação no Windows (PowerShell)

Abra o PowerShell na pasta do projeto e crie um ambiente virtual:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
ou tente:
```.\.venv313\Scripts\Activate.ps1```
Se a execução de scripts estiver bloqueada no PowerShell, libere-a apenas para a sessão atual e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Em Linux ou macOS, a ativação do ambiente é feita com:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuração

Antes de executar, abra `config.py` e confira principalmente estas opções:

| Opção | Função |
|---|---|
| `CSV_PATH` | caminho do arquivo CSV de entrada |
| `PASTA_SAIDA_DIR` | pasta na qual as imagens serão salvas |
| `COL_ESPECIE` | nome exato da coluna de espécie no CSV |
| `COL_CATEGORIA` | nome da coluna usada para separar e filtrar categorias |
| `CATEGORIAS` | categorias processadas; use `None` para todas |
| `LIMITE_ESPECIES` | limita o número de linhas para testes; use `None` para todas |
| `IMAGENS_POR_ESPECIE` | quantidade desejada por espécie |
| `TAMANHO` | tamanho solicitado: `square`, `small`, `medium`, `large` ou `original` |
| `LICENCAS` | licenças aceitas na consulta |
| `SO_GRAU_PESQUISA` | restringe a observações com grau de pesquisa |
| `PLACE_ID` | restringe a uma localidade do iNaturalist; `None` desativa o filtro |

### Caminhos portáveis

O projeto usa caminhos relativos à sua própria pasta, por meio de `BASE_DIR`. Assim, ele continua funcionando depois de ser movido ou clonado em outro computador:

```python
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "fauna_parque_das_dunas_reduzido_v2.csv"
PASTA_SAIDA_DIR = BASE_DIR / "imagens_dataset"
```

### Teste pequeno antes do download completo

Downloads de centenas de imagens por espécie podem consumir bastante tempo, banda e disco. Para a primeira execução, use por exemplo:

```python
CATEGORIAS = ["Mamíferos"]
LIMITE_ESPECIES = 2
IMAGENS_POR_ESPECIE = 5
```

Depois que o teste funcionar, aumente os valores gradualmente.

## Formato esperado do CSV

O arquivo deve estar em UTF-8 e conter ao menos a coluna indicada em `COL_ESPECIE`. Com a configuração atual, as colunas relevantes são `Categoria` e `Espécie`:

```csv
Categoria,Espécie
Anfíbios,Rhinella sp.
Aves,Egretta thula
Mamíferos,Callithrix jacchus
```

As demais colunas podem permanecer no arquivo; elas não interferem no processamento atual.

## Como executar

Com o ambiente virtual ativado e o `config.py` revisado:

```powershell
python main.py
```

Sem argumentos, o programa mantém o comportamento original: lê o CSV e aplica os filtros definidos em `config.py`.

### Buscar uma espécie diretamente

Use `--especie` para processar apenas um nome científico, sem ler o CSV:

```powershell
python main.py --especie "Callithrix jacchus"
```

Para escolher também a quantidade desejada:

```powershell
python main.py --especie "Callithrix jacchus" --quantidade 20
```

Nesse modo, como não há uma categoria vinda do CSV, a pasta da espécie é criada diretamente dentro de `PASTA_SAIDA_DIR`. O argumento `--quantidade` também pode ser usado no processamento do CSV para substituir temporariamente `IMAGENS_POR_ESPECIE`:

```powershell
python main.py --quantidade 10
```

Para consultar todas as opções:

```powershell
python main.py --help
```

### Executar os testes

Os testes da CLI não fazem chamadas de rede nem baixam imagens:

```powershell
python -m unittest discover -s tests -v
```

O programa exibe o andamento no terminal. Uma estrutura de saída típica é:

```text
imagens_dataset/
└── Mamíferos/
    └── Callithrix_jacchus/
        ├── Callithrix_jacchus_123456_cc-by.jpg
        └── Callithrix_jacchus_789012_cc-by-nc.jpg
```

O nome de cada imagem inclui a espécie normalizada, o ID da observação no iNaturalist e a licença informada pela foto.

### Continuar um download interrompido

Basta executar `python main.py` novamente. O projeto consulta os arquivos presentes na pasta da espécie e ignora nomes já existentes. Espécies cuja pasta já atingiu `IMAGENS_POR_ESPECIE` também são puladas.

## Problemas comuns

### `ModuleNotFoundError: No module named 'pandas'` ou `'requests'`

Ative o ambiente virtual e instale as dependências:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### `Arquivo CSV não encontrado`

Revise `CSV_PATH` em `config.py`. O caminho deve apontar para um arquivo existente.

### Nenhuma espécie é processada

Confira se:

- o texto em `CATEGORIAS` é idêntico ao texto da coluna `Categoria`, inclusive acentos;
- `COL_ESPECIE` e `COL_CATEGORIA` correspondem exatamente aos cabeçalhos do CSV;
- o CSV foi salvo em UTF-8;
- `LIMITE_ESPECIES` não está definido como zero.

### Táxon não encontrado

O projeto exige uma correspondência exata do nome científico ou de um sinônimo retornado pelo iNaturalist. Verifique a grafia e teste o nome diretamente no site do iNaturalist. Entradas como `sp.` são tratadas como busca pelo gênero.

### Poucas imagens são baixadas

Pode não haver imagens suficientes que atendam simultaneamente à licença, ao grau de pesquisa e à localidade configurados. Tente revisar `LICENCAS`, `SO_GRAU_PESQUISA` e `PLACE_ID`, respeitando os requisitos de uso do dataset.

## Melhorias sugeridas

### 1. Busca direta pelo nome da espécie (implementada)

O programa aceita uma espécie pela linha de comando:

```powershell
python main.py --especie "Callithrix jacchus" --quantidade 20
```

O comportamento é:

```text
--especie informado  -> processa apenas o nome digitado
--especie ausente    -> mantém o fluxo atual baseado no CSV
```

Isso preserva compatibilidade com o uso existente e torna o programa útil para consultas pontuais. Evoluções futuras podem acrescentar `--categoria`, `--saida` e uma confirmação dos dados do táxon antes do download.

### 2. Caminhos portáveis (implementada)

`CSV_PATH` e `PASTA_SAIDA_DIR` são formados a partir de `BASE_DIR`, eliminando a dependência de um caminho específico da máquina.


## Uso responsável

As imagens pertencem aos respectivos autores e mantêm suas licenças originais. Antes de publicar ou redistribuir o dataset, confira as condições de cada licença, preserve as informações de autoria e documente os filtros usados na coleta. Também respeite os limites e as boas práticas de uso da API do iNaturalist.

