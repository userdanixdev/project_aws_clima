import boto3
from datetime import datetime
from rich import print
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

def serializacao(obj):
    """ Serializa qualquer tipo de dados em formato JSON """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj,dict):
        return {k: serializacao(v) for k, v in obj.items()}
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

def normalizar_resposta_aws(response):
    return {
        "request_id": response["ResponseMetadata"]["RequestId"],
        "status_code": response["ResponseMetadata"]["HTTPStatusCode"],
        "region": response["ResponseMetadata"]["HTTPHeaders"].get("x-amz-id-2"),
        "bucket_count": len(response.get("Buckets", [])),
        "first_bucket": response["Buckets"][0]["Name"] if response.get("Buckets") else None,
    }    

## Uso do rich:

console = Console()

def print_analytics(data: dict):
    table = Table(title="AWS S3 ANALYTICS", show_lines=True)

    table.add_column("Campo", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")

    for k, v in data.items():
        table.add_row(str(k), str(v))

    console.print(table)

def print_structured(data: dict):
    console.print(
        Panel(
            Pretty(data),
            title="S3 STRUCTURED RESPONSE",
            expand=False
        )
    )

def print_raw(response: dict):
    console.print(
        Panel.fit(
            Pretty(response),
            title="RAW AWS RESPONSE",
            border_style="red"
        )
    )

# EXECUÇÃO (MAIN)

s3 = boto3.client("s3")
resposta = s3.list_buckets()

structured_data = response_structure(resposta)
analytics_data = normalizar_resposta_aws(resposta)  

console.rule("[bold blue]AWS S3 REPORT")

print_analytics(analytics_data)

console.rule("[bold green]STRUCTURED DATA")
print_structured(structured_data)

console.rule("[bold yellow]RAW RESPONSE")
print_raw(resposta)