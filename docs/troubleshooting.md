# Troubleshooting – Pipeline AWS Clima
---
## Desafios Encontrados Durante o Desenvolvimento

Durante a construção do pipeline de ingestão de dados climáticos, diversos desafios técnicos foram identificados. A análise e resolução desses problemas contribuíram para o entendimento prático de conceitos importantes de Engenharia de Dados, Data Lakes e serviços da AWS.

### 1. Configuração de Credenciais AWS em Ambiente Local

Ao executar a função Lambda localmente utilizando boto3, ocorreu o erro:

```text
Unable to locate credentials
```

O problema ocorreu porque o SDK da AWS necessita de credenciais válidas para acessar o Amazon S3 em ambiente local. Foi identificado que esse comportamento é esperado, já que em produção a autenticação da Lambda é realizada por meio de IAM Roles.

**Aprendizado:**

* Diferença entre autenticação local e autenticação em ambiente AWS.
* Uso de IAM Roles para acesso seguro aos serviços da AWS.

---

### 2. Configuração do Amazon Athena

Durante a primeira tentativa de execução de consultas no Athena, ocorreu o erro relacionado à ausência de local para armazenamento dos resultados das consultas.

**Solução:**

* Configuração de um bucket S3 para armazenamento dos resultados do Athena.

**Aprendizado:**

* Entendimento do funcionamento dos Workgroups e da persistência dos resultados de consultas no Athena.

---

### 3. Colunas Duplicadas no Glue Catalog

Após a execução do Glue Crawler, o Athena retornou o erro:

```text
HIVE_INVALID_METADATA:
Table descriptor contains duplicate columns
```

Foi identificado que os campos `source`, `date` e `location` estavam sendo reconhecidos simultaneamente como colunas do arquivo JSON e como colunas de particionamento do Data Lake.

**Aprendizado:**

* Diferença entre colunas de dados e colunas de partição.
* Importância do desenho correto da estrutura de diretórios no S3.

---

### 4. Problemas de Inferência Automática de Schema

O Glue Crawler inferiu automaticamente estruturas complexas presentes no JSON retornado pela Visual Crossing Weather API, especialmente no campo:

```json
payload.stations
```

Como cada cidade possui estações meteorológicas diferentes, cada partição passou a apresentar um schema distinto.

Isso resultou no erro:

```text
HIVE_PARTITION_SCHEMA_MISMATCH
```

**Aprendizado:**

* Limitações da inferência automática de schemas em estruturas JSON altamente dinâmicas.
* Importância da padronização de schemas para ambientes analíticos.

---

### 5. Estruturas Complexas para Consulta Analítica

O campo `payload` continha múltiplos níveis de objetos aninhados (`struct`) e arrays (`array<struct>`), dificultando consultas diretas no Athena.

**Aprendizado:**

* Diferença entre armazenamento operacional e armazenamento analítico.
* Necessidade de transformação dos dados para formatos mais adequados ao consumo analítico.

---

## Evidência de Validação

📊 Validação inicial da camada Raw após refatoração

![Athena validation](images/shot_athena.png)

---

## Próximos Passos

- Armazenar payload como JSON bruto na Raw
- Criar camada Silver com dados tratados
- Converter para Parquet
- Melhorar performance no Athena com Glue

---

## Conclusão

Esses desafios consolidaram conhecimentos em AWS Lambda, S3, Glue, Athena e arquitetura de Data Lakes.

---

