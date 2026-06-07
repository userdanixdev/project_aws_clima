import boto3
import json
import os
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Capitais brasileiras 
DEFAULT_LOCATIONS = [
    "Rio Branco, BR",
    "Maceio, BR",
    "Macapa, BR",
    "Manaus, BR",
    "Salvador, BR",
    "Fortaleza, BR",
    "Brasilia, BR",
    "Vitoria, BR",
    "Goiania, BR",
    "Sao Luis, BR",
    "Cuiaba, BR",
    "Campo Grande, BR",
    "Belo Horizonte, BR",
    "Belem, BR",
    "Joao Pessoa, BR",
    "Curitiba, BR",
    "Recife, BR",
    "Teresina, BR",
    "Rio de Janeiro, BR",
    "Natal, BR",
    "Porto Alegre, BR",
    "Porto Velho, BR",
    "Boa Vista, BR",
    "Florianopolis, BR",
    "Sao Paulo, BR",
    "Aracaju, BR",
    "Palmas, BR",
]

# Endpoint da API Visual Crossing.
BASE_URL = (
    "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
    "/timeline"
)


def normalizar_valor_particao(valor):

    """ Converte o nome da cidade para formato compatível com particionamentos da AWS
     Ex: 'São Paulo, BR' -> 'sao_paulo_br' 
     
     Isso evita problemas com espaços, acentos, caracteres especiais
     """

    # remove acentos transformando caracateres Unicode em sua representação ASCII equivalente
    valor_normalizado = unicodedata.normalize("NFKD", valor)
    # Converte para ASCII removendo caracteres incompatíveis
    valor_ascii = valor_normalizado.encode("ascii", "ignore").decode("ascii")
    
    # A função retorna valores minúsculos e remove caracteres que podem causar problemas em partições:
    return (
        valor_ascii.lower()
        .replace(",", "")
        .replace("/", "-")
        .replace(" ", "_")
    )


def get_locations():
    """ Obtém a lista de cidades a partir da variável de ambiente LOCATIONS
    
    Formato esperado: Cidade1;Cidade2;Cidade3
    
    Caso não existe configuração, utiliza a lista padrão
    """
    locations = os.environ.get("LOCATIONS")
    if not locations:
        return DEFAULT_LOCATIONS
# A função divide a string utilizando ';' como separador.
    return [location.strip() for location in locations.split(";") if location.strip()]


def fetch_weather(location, start_date, end_date, api_key):
    """ 
    Realiza a chamada da API Visual Crossing e retorna JSON convertido em dict Python"""

    # URLs não aceitam alguns caracteres especiais.
    # Codifica caracteres especiais das cidade para a URL
    encoded_location = urllib.parse.quote(location)
    # Montagem os parâmetros da requisição:
    query_params = urllib.parse.urlencode(
        {
            # Temperatura em Celsius
            "unitGroup": "metric",
            # Retorna informações diárias
            "include": "days",
            # Formato da resposta
            "contentType": "json",
            # Chave de autentição
            "key": api_key,
        }
    )
    # Montagem da URL final da requisição:
    url = f"{BASE_URL}/{encoded_location}/{start_date}/{end_date}?{query_params}"
    # Montagem da requisição HTTP:
    request = urllib.request.Request(url, headers={"User-Agent": "aws-lambda-weather-etl"})
    # Chamada para a API:
    with urllib.request.urlopen(request, timeout=30) as response:
        # Retorna o SON recebido em dicionário Python:
        return json.loads(response.read().decode("utf-8"))


def lambda_handler(evento, context):
    """
    Lambda responsável por:
    
    1. Consultar a previsão do tempo na API Visual Crossing.
    2. Armazenar os dados brutos (RAW) no Amazon S3
    3. Organizar os arquivos em partições compatíveis com Glue/Athena
    4. Registrar sucessos e falhas da execução
    """

    # Variáveis de ambiente:
    api_key = os.environ["VISUAL_CROSSING_API_KEY"]
    bucket_name = os.environ["BUCKET_NAME"]
    
    # Fuso horário utilizado para padronização das datas:
    fuso_horario = ZoneInfo(os.environ.get("TIMEZONE", "America/Sao_Paulo"))

# A API será consutada para a data atual e de amanhã permitindo capturar previsão atual e próxima previsão
    # Data/hora atual:
    now = datetime.now(fuso_horario)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    # Datas utilizadas na consulta da API:
    start_date = today.strftime("%Y-%m-%d")
    end_date = tomorrow.strftime("%Y-%m-%d")

    # Partição baseada na data de ingestão:
    partition_date = today.strftime("%Y-%m-%d")

    # Momento exato da extração:
    extraction_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Timestamp utilizado para garantir nomes únicos de arquivos:
    file_timestamp = now.strftime("%Y%m%d%H%M%S")

 # O boto3 é o SDK oficial da AWS para Python.
    cliente_s3 = boto3.client("s3")
    successes = []
    failures = []

# Itera por cada cidade individualmente em get_locations.
# Percorre todas as cidades configuradas para ingestão. Para cada cidade:
# 1. Consulta a API Visual Crossing.
# 2. Monta o registro RAW.
# 3. Salva um arquivo JSON no S3.
    for location in get_locations():
        city_partition = normalizar_valor_particao(location)
# Python irá consultar cada valor das partições encontrada, inclusice os parâmetros de consultas
        try:
            payload = fetch_weather(location, start_date, end_date, api_key)

# Estrutura que será armazenada a camada RAW. Dados preservados sem transformação:
            raw_registros = {
                # "source": "visual_crossing",
# O Athena interpreta como uma coluna duplicada com outra 'source' de Particionamento.
# Dessa forma, retirada da ingestão.
                "location_requested": location,
                # Endereço padronizado retornado pelo API
                "location_resolved": payload.get("resolvedAddress"),
#                "start_date": start_date,
# Removido por ser reduntante e podem ser obtidas pelo particionamento e pelo payload
#                "end_date": end_date,
# Removido por ser reduntante e podem ser obtidas pelo particionamento e pelo payload.

                # Data e hora exata em que os dados foram extraídos da fonte externa.
                "extraction_timestamp": extraction_timestamp,
                #"payload": payload,
                "payload_json":json.dumps(payload, ensure_ascii=False)
            }
# O problema que o serviço da AWS Glue tenta interpretar todo o JSON da API. Cada cidade possui
# estações diferentes. A correção será o JSON como texto. Dessa forma o Glue irá exergar tudo como string.
# Sem STRUCT aninhada e conflito de schema entre as cidades e entre partições.
#  Assim não aparecerá o erro: HIVE_PARTITION_SCHEMA_MISMATCH            
# Além disso o Athena irá exergar como VARCHAR 

### A variável 'object_key' é estruturada para Data Lake em particionamento para facilidade de filtros
## por data e cidade e melhor desempenho de ferramentas de leituras em SQL como o Athena.

            object_key = (
                f"raw/clima/"
                f"source=visual_crossing/"
                f"date={partition_date}/"
                f"location={city_partition}/"
                f"weather_{file_timestamp}.json"
            )
# Cria um cliente S3 utilizando as permissões IAM associadas à execução da Lambda.
# Não é necessário informar Access Key ou Secret Key, pois a autenticação é realizada automaticamente
# pela Role da função Lambda.
            # Grava arquivo RAW no S3:
            cliente_s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=json.dumps(raw_registros, ensure_ascii=False).encode("utf-8"),
                ContentType="application/json"
            )

            successes.append({
                "location": location,
                "s3_key": object_key
            })

            print(
                f"Arquivo salvo: "
                f"s3://{bucket_name}/{object_key}"
            )

# Tratamento de erros:
        except urllib.error.HTTPError as error:
            error_message = error.read().decode("utf-8")

            failures.append({
                "location": location,
                "error_type": "HTTPError",
                "status_code": error.code,
                "message": error_message
            })

            print(f"HTTP error for {location}: {error.code} - {error_message}")

        except Exception as error:
            failures.append({
                "location": location,
                "error_type": type(error).__name__,
                "message": str(error)
            })

            print(f"Error for {location}: {error}")

    # 200 = sucesso total
    # 207 = sucesso parcial (algumas cidades falharam)
    status_code = 200 if not failures else 207
# Retorno padrão da Lambda. Este retorno pode ser consumido por CloudWatch Logs, EventBridge,
# Step Functions e testes locais que serão usados no desenvolvimento do projeto.
# Retorno final da execução contém a data da partição processada, quantidade de sucessos
# quantidade de falhas e detalhes das cidades processadas
# Essas informações ficam disponíveis no resultado da execução da Lambda e nos logs do CloudWatch.
    return {
        "statusCode": status_code,
        "body": json.dumps(
            {
                "message": "Weather ingestion finished",
                "partition_date": partition_date,
                "success_count": len(successes),
                "failure_count": len(failures),
                "successes": successes,
                "failures": failures
            },
            ensure_ascii=False
        )
    }