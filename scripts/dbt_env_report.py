import json
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

session = boto3.Session()
glue = boto3.client("glue")
s3 = boto3.client("s3")

bucket_name = os.getenv("BUCKET_NAME")

if not bucket_name:
    raise ValueError("BUCKET_NAME não encontrado no .env")

# Region
region_name = session.region_name

# Threads
threads = os.cpu_count()

# Schema (Glue Database)
response = glue.get_databases()

databases = [
    db["Name"]
    for db in response["DatabaseList"]
]

# Criação dos prefixes do dbt
for folder in ["metadata/", "tables/"]:
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=folder,
        )
        print(f" {folder} criado")
    except Exception as e:
        print(f" Erro criando {folder}: {e}")

config = {
    "region_name": region_name,
    "database": "AwsDataCatalog",
    "schema": databases[0] if databases else None,
    "s3_staging_dir": f"s3://{bucket_name}/metadata/",
    "s3_data_dir": f"s3://{bucket_name}/tables/",
    "threads": threads,
}

# Exibe no terminal
print(json.dumps(config, indent=4))

# Salva relatório
report_file = REPORT_DIR / "dbt_env_report.json"

with open(report_file, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print(f"\n Relatório salvo em: {report_file}")
