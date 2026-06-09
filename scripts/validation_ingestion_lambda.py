from dotenv import load_dotenv
import os
import json
import boto3
from collections import defaultdict
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

VALIDATION_FILE = REPORT_DIR / "validacao_lambda.json"

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
PREFIX = "raw/clima"

def validar_ingestao():
    s3 = boto3.client("s3")
    paginador = s3.get_paginator("list_objects_v2")
# A variável cria um paginator para percorrer todos objetos do bucket.    
    total_arquivos = 0
    particoes = defaultdict(int)
# Aqui o dicionário armazenará a quantidade de arquivos por partição encontrada.   

# O loop percorre todas as páginas retonadas pela AWS    
    for page in paginador.paginate(
        Bucket=BUCKET_NAME,
        Prefix=PREFIX):
# Cada página encontrada possui uma lista de objetos em 'Contents', caso não, retorna vazio.        
        for obj in page.get("Contents",[]):
            key = obj["Key"] # Obtém o caminho completo do objeto no Bucket S3 AWS
            total_arquivos += 1  # Contagem caso encontre objetos
            partes = key.split("/") # Divide o caminho em separadores por '/'
# Procura o elemento que inicia com 'date=' e o next() retorna o primeiro valor encontrado
# Caso não encontre, retonrna 'date=desconhecida'            .
            data = next(
                (p for p in partes if p.startswith("date=")),
                "date=desconhecida"
            )
            cidade = next(
                (p for p in partes if p.startswith("location=")),
                "location=desconhecida"
            )
            particoes[f"{data}/{cidade}"] += 1
    # Cria uma chave composta com date e location e soma para cada arquivo encontrado na partição            

# Resultados na tela terminal:
    print("\n=== VALIDAÇÃO DA INGESTÃO ===")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Total de arquivos: {total_arquivos}")
    print(f"Total de partições: {len(particoes)}")
    print("\nPartições encontradas:\n")
    # Exibe cada partição e sua quantidade de arquivos:
    for particao, quantidade in sorted(particoes.items()):
        print(f"{particao} -> {quantidade} arquivo(s)")
# Estrutura da evidência da validação:
    relatorio = {
        "bucket": BUCKET_NAME,
        "prefix": PREFIX,
        "total_arquivos": total_arquivos,
        "total_particoes": len(particoes),
        "particoes": dict(particoes),
        "validation_timestamp":datetime.now().isoformat()
    }
    # Salva o relatório em JSON para auditoria e documentação:
    VALIDATION_FILE.write_text(
    json.dumps(relatorio, indent=4, ensure_ascii=False),
    encoding="utf-8"
)
    print(f"\nRelatório salvo em: {VALIDATION_FILE}")    

if __name__ == "__main__":
    validar_ingestao()


