{% docs __overview__ %}

# 🌤️ Projeto ClimaBR - Pipeline de Dados Meteorológicos na AWS

O ClimaBR é um projeto de Engenharia de Dados desenvolvido para coletar, transformar e analisar dados meteorológicos históricos e de previsão utilizando uma arquitetura moderna baseada em AWS, dbt e Amazon Athena.

Os dados são obtidos pela API da Visual Crossing e processados em múltiplas camadas analíticas, permitindo a geração de indicadores climáticos confiáveis e análises comparativas entre previsão e dados observados.

## 📌 Objetivos:

- Coletar dados meteorológicos históricos e de previsão
- Ingerir, padronizar e enriquecer dados climáticos históricos e de previsão
- Estruturar uma arquitetura em camadas no dbt para análises confiáveis
- Medir desvios entre previsão e dados observados
- Gerar indicadores mensais por cidade e períodos com agregações climáticas

### 🏗️ Arquitetura

Visual Crossing API → AWS Lambda → Amazon S3 → AWS Glue Catalog → Amazon Athena → dbt → Camada Analítica

## 🧱 Estrutura do Projeto:
```
├── models/
│   ├── staging/
│   │   └── stg_clima.sql               # Modelo raw dos dados da API
│   ├── intermediate/
│   │   └── int_clima_diario.sql        # Enriquecimento dos dados climáticos
│   └── marts/
│       ├── fct_analise_mensal.sql     # Fato mensal de métricas climáticas
│       └── fct_desvio_previsao.sql    # Fato com desvio entre previsão e combinado
│
```

### 🛠️ Tecnologias:

- Python
- AWS Lambda
- Amazon S3
- AWS Glue
- Amazon Athena
- dbt Core
- Poetry
- Visual Crossing Weather API

## 🗃️ Fontes de Dados:

[Visual Crossing Weather ApI](https://www.visualcrossing.com/weather-data-pricing/)

## 🔍 Exemplos de Métricas:

## Métricas Aplicadas no Projeto

### Temperatura
- Temperatura média diária
- Temperatura máxima e mínima
- Amplitude térmica

### Sensação Térmica
- Sensação térmica média
- Diferença entre sensação térmica e temperatura

### Umidade
- Umidade média diária
- Variação de umidade

### Precipitação
- Precipitação total diária
- Precipitação acumulada
- Quantidade de dias com chuva

### Radiação Solar
- Índice UV médio
- Horas de sol

### Vento
- Velocidade média do vento
- Rajada máxima

### Cobertura do Céu
- Cobertura média de nuvens

### Visibilidade
- Visibilidade média diária

### Qualidade da Previsão
- Desvio entre valor previsto e realizado
- Erro Absoluto Médio (MAE)
- Erro Percentual
- Acurácia da previsão

### Análises por Cidade
- Temperatura média por cidade
- Total de precipitação por cidade
- Ranking de cidades mais quentes
- Ranking de cidades mais chuvosas

### Indicadores Executivos
- Cidade mais quente do período
- Cidade mais fria do período
- Cidade com maior precipitação
- Cidade com maior índice UV

---

## 👨‍💻 Autor

**ClimaBR by Daniel Martins**
Engenharia de Dados | Amazon AWS | dbt | Athena 

{% enddocs %}
