import boto3
#from boto3 import session
from datetime import datetime
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from pathlib import Path
import json 


BASE_DIR = Path(__file__).resolve().parent

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

JSON_FILE = REPORT_DIR / "aws_report.json"


def serializacao(obj):
    """ Serializa qualquer tipo de dados em formato JSON """
# a função 'isinstance' verifica qual é o tipo do objetivo    
# melhor do que 'type' porque serve como herença
    if isinstance(obj, datetime):
        return obj.isoformat()
# isoformat converte data/hota para string padrão ISO 8601
# json não armazena objetos 'datetime' e pode gerar erro.    
    if isinstance(obj,dict):
        return {k: serializacao(v) for k, v in obj.items()}
# na dict comprehension temos um loop que em que 'items' retorna pares chave-valor
# assim chamo a função 'serialização' para percorrerr 'k e v' 
# Assim permite processar qualquer estrutura aninhada    
    if isinstance(obj, list):
        return[serializacao(i) for i in obj]
    return obj

def response_structure(response:dict) -> dict:
    structured = {
        "response_metadata":serializacao(response.get("ResponseMetadata")),
        "buckets":serializacao(response.get("Buckets")),
        "owner":serializacao(response.get("Owner")),
        "total_buckets":len(response.get("Buckets",[])),
        "raw":serializacao(response)
    }
    return structured

def normalizar_resposta_aws(response:dict,region:str) -> dict:
    return {
        "request_id": response["ResponseMetadata"]["RequestId"],
        "status_code": response["ResponseMetadata"]["HTTPStatusCode"],
        "region": response["ResponseMetadata"]["HTTPHeaders"].get("x-amz-id-2"),
        "region_real": region,
        "bucket_count": len(response.get("Buckets", [])),
        "first_bucket": response["Buckets"][0]["Name"] if response.get("Buckets") else None,
    }    

## Uso do rich: Serve para exibir dados no terminal de forma mais bonita e organizada
# em vez de usar varios prints sem formatação

# Classe que deve ser declarada, ponto de partida inicial
console = Console() # Necessário criar o objeto 'console' para exibir os elementos
# formatados no teminal

def print_analytics(data: dict):
    table = Table(title="AWS S3 ANALYTICS", show_lines=True)
# Criação da classe 'table'mostrando as linhas separadas por cada registro    

    table.add_column("Campo", style="cyan", no_wrap=True)
# adiciona uma tabela com a cor AZUL e 'no_wrap' impede a quebra de linha    
    table.add_column("Valor", style="green")
# Percorre todos os pares chave-valor do dicionárioo
    for k, v in data.items():
        table.add_row(str(k), str(v))
# Dentro do looping, adiciona cada linha em string de 'k e v'
    console.print(table)
# Mostra a tabela
# Essa função recebe um dicionário e deverá exibir uma estrutura formatada:
def print_structured(data: dict):
# Assim, com a classe 'console' deverá exibir no terminal
    console.print(
        Panel( # Cria uma caixa com bordas
            Pretty(data), # formata os dados com identação e quebra de linhas
            title="S3 STRUCTURED RESPONSE",
            expand=False
        )# Expand=False mostra o título centralizado ocupando apenas espaço necessário
    )

def print_raw(response: dict):
    console.print(
        Panel.fit(
            Pretty(response),
            title="RAW AWS RESPONSE",
            border_style="red"
        )
    )

# EXECUÇÃO:
session = boto3.Session()
s3 = boto3.client("s3")
resposta = s3.list_buckets()

structured_data = response_structure(resposta)
analytics_data = normalizar_resposta_aws(resposta,session.region_name)  

def gerar_relatorio():
    console.rule("[bold blue]AWS S3 REPORT")
    print_analytics(analytics_data)

    console.rule("[bold green]STRUCTURED DATA")
    print_structured(structured_data)

    console.rule("[bold yellow]RAW RESPONSE")
    print_raw(resposta)

gerar_relatorio()
# Captura tudo que foi exibido no terminal
with console.capture() as capture:
    gerar_relatorio()

# Salva o conteúdo no arquivo. Se existir é sobrescrito
JSON_FILE.write_text(
    json.dumps(structured_data, indent=4, ensure_ascii=False),
    encoding="utf-8"
)  # Saída com resposta estruturada para análise e automação em JSON.
console.print(f"Relatórios salvos em: {REPORT_DIR}")