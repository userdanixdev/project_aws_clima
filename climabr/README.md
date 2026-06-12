🌦️ climaBR — Pipeline de Transformação de Dados com dbt (AWS Athena)

📌 Visão Geral

O climaBR é a camada de transformação do pipeline de dados climáticos da AWS.

Utiliza dbt sobre Amazon Athena para transformar dados brutos ingeridos via AWS Lambda em modelos analíticos confiáveis, estruturados e prontos para consumo.

O projeto segue arquitetura moderna de ETL (Extract → Transform → Load).

### 🏗️ Arquitetura do Pipeline:
```
AWS Lambda (Ingestão)
        ↓
S3 (Landing / Raw Data)
        ↓
dbt (Transformações)
        ↓
Athena (Query Engine)
        ↓
Intermediate Models → Marts (Analytics Layer)
```

## 🧱 Camadas de Dados:
### 📥 Landing (Raw)

Dados brutos vindos da AWS Lambda, sem transformação e base histórica no S3.

### 🔄 Staging (staging):

- Limpeza e padronização
- Renomeação de colunas
- Conversão de tipos
- Deduplicação inicial

``` Exemplo: stg_clima```

### ⚙️ Intermediate (intermediate):

- Aplicação de regras de negócio
- Criação de colunas derivadas (CASE WHEN)
- Enriquecimento dos dados
- Base confiável para analytics

```Exemplo: int_clima_diario```

### 📊 Marts (futuro):

- Camada final para BI
- KPIs e métricas agregadas
- Dataset pronto para dashboards

### ⚙️ Tecnologias:

- dbt-core 1.11+
- dbt-athena-adapter
- AWS S3
- AWS Athena
- AWS Lambda
- AWS Glue Data Catalog
- dbt tests (schema + custom)
- Configuração

1. Instalar dependências
```poetry install``` ( Opcional )

2. Configurar profile dbt
```
climabr:
  outputs:
    dev:
      type: athena
      database: AwsDataCatalog
      schema: landing
      region_name: us-east-2
      s3_data_dir: s3://seu-bucket/tables/
      s3_staging_dir: s3://seu-bucket/metadata/
      threads: 1
```
3. Executar modelos

```dbt run```

Por camada:

```
dbt run --select staging
dbt run --select intermediate
```

4. Executar testes

```dbt test```

## 🧪 Qualidade de Dados

O projeto garante qualidade com:

1. Testes automáticos

- not_null
- accepted_values

2. Regras de negócio


- Consistência entre staging e intermediate

## 🔍 Exemplo de Transformação:

Classificação de temperatura:
```sql
CASE
  WHEN temperatura < 10 THEN 'frio'
  WHEN temperatura BETWEEN 10 AND 25 THEN 'ameno'
  ELSE 'quente'
END AS faixa_temperatura
🧪 Validação de CASE WHEN
SELECT *
FROM intermediate.int_clima_diario
WHERE
  (temperatura < 10 AND faixa_temperatura <> 'frio')
  OR (temperatura BETWEEN 10 AND 25 AND faixa_temperatura <> 'ameno')
  OR (temperatura > 25 AND faixa_temperatura <> 'quente');
```

## 🚀 Objetivos:

- Construir pipeline confiável de dados climáticos
- Garantir consistência entre camadas
- Aplicar boas práticas de dbt e ELT moderno
- Criar base sólida para BI e análises

---

### 📁 Estrutura:
```
climaBR/
│
├── models/
│   ├── staging/
│   ├── intermediate/
│   └── marts/
│
├── tests/
├── macros/
├── dbt_project.yml
└── README.md
```

### 🏷️ Release:

```
Versão atual: v0.1.4
Próxima release: v0.1.5 (dbt quality & marts expansion)
```

### 👨‍💻 Autor

Pipeline de dados desenvolvido com foco em engenharia de dados moderna na AWS utilizando dbt, Athena e boas práticas de modelagem ELT.

### ⭐ Destaques do Projeto:

- Arquitetura ETL moderna
- Camadas bem definidas (staging → intermediate → marts)
- Regras de negócio auditáveis
- Testes automatizados com dbt
- Pronto para escala em produção