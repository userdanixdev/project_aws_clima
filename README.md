# 🌦️ Project AWS Clima

![Python](https://img.shields.io/badge/Python-3.12-blue)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange)
![Amazon S3](https://img.shields.io/badge/Amazon-S3-green)
![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Projeto de engenharia de dados para coleta, ingestão e armazenamento de dados climáticos utilizando **Python**, **Visual Crossing Weather API**, **AWS Lambda** e **Amazon S3**.

Este projeto está sendo desenvolvido com foco em boas práticas de engenharia de dados, versionamento, organização de ambiente, segurança de credenciais e preparação para construção de um pipeline completo em nuvem.

---

## 🎯 Objetivo do Projeto

O objetivo principal é construir um pipeline de dados climáticos capaz de:

- consumir dados de uma API meteorológica;
- validar a requisição localmente;
- executar a ingestão em uma função AWS Lambda;
- armazenar os dados brutos no Amazon S3;
- organizar os arquivos com particionamento;
- preparar a base para consultas futuras com AWS Glue, Athena ou Spark.

A primeira etapa do projeto foca na camada **raw/bronze**, onde os dados são armazenados próximos ao formato original retornado pela API.

---

## 🌍 Sobre APIs Climáticas

Durante a análise inicial foram consideradas duas APIs:

### OpenWeather

A OpenWeather, disponível em `openweathermap.org`, é uma API bastante conhecida para dados meteorológicos. Ela oferece endpoints para clima atual, previsão, geocoding, qualidade do ar e outros produtos climáticos.

Ela é uma boa opção para aplicações que precisam consultar clima em tempo real ou construir dashboards simples.

### Visual Crossing

A Visual Crossing Weather API foi escolhida para este projeto por ser mais adequada ao contexto de engenharia de dados.

Ela permite consultar dados climáticos usando uma estrutura simples e flexível, com suporte a:

- dados atuais;
- previsão do tempo;
- histórico climático;
- consulta por localização;
- consulta por latitude e longitude;
- retorno em JSON;
- uso em pipelines de dados.

Neste projeto, a localização inicial utilizada foi São Paulo via latitude e longitude:

```-23.5505,-46.6333```

## 🌍 Sobre as Fontes de Dados Climáticos

Durante a etapa inicial do projeto foram analisadas duas APIs climáticas diferentes: **OpenWeather** e **Visual Crossing**.

É importante destacar que elas são serviços independentes. A Visual Crossing não pertence à OpenWeather e não é uma extensão da OpenWeather. Cada uma possui sua própria plataforma, documentação, chave de API, endpoints, limites de uso e estrutura de resposta.

### Por que a Visual Crossing foi escolhida?

A Visual Crossing foi escolhida neste projeto porque oferece uma estrutura simples para ingestão de dados em pipelines.

Para engenharia de dados, isso é útil porque facilita:

- extração de dados por período;
- armazenamento do payload bruto;
- criação de partições por data e localização;
- integração com S3;
- evolução futura para Glue, Athena e camadas tratadas.

### 🛠️ Tecnologias Utilizadas:

- Python 3.12
- Poetry para gerenciamento de dependências
- python-dotenv para leitura de variáveis locais
- boto3 para integração com serviços AWS
- ruff para qualidade e padronização do código
- pytest para testes
- AWS Lambda
- Amazon S3
- Visual Crossing Weather API
- Git e GitHub

### 📁 Estrutura Inicial do Projeto:
```
project_aws_clima/
├── scripts/
│   └── test_visual_crossing_request.py
├── lambda_function.py
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
└── poetry.lock
```

## Descrição dos arquivos:

| Arquivo |	 Função | 
|--|--| 
scripts/test_visual_crossing_request.py	|Script local para validar a conexão com a API
lambda_function.py | 	Arquivo reservado para a função AWS Lambda
.env.example |	Modelo das variáveis de ambiente necessárias
.gitignore | Define arquivos que não devem ser versionados
pyproject.toml |	Configuração do projeto Poetry
poetry.lock |	Controle exato das versões instaladas
README.md |	Documentação do projeto
LICENSE	| Licença do projeto

## 📦 Dependências Instaladas:

### Dependências principais

```poetry add boto3```

*O boto3 será utilizado para integração com a AWS, principalmente para gravar arquivos no Amazon S3.*

### Dependências de desenvolvimento:

```poetry add --group dev pytest python-dotenv ruff```

*Essas dependências foram adicionadas para apoiar desenvolvimento, testes e qualidade do código.*

## 🔐 Variáveis de Ambiente:

O projeto utiliza um arquivo .env local, que não deve ser versionado. O arquivo .env.example serve como modelo seguro.

## 🧪 Teste Local da API:

Antes de construir a Lambda, foi criado um script local para validar a conexão com a Visual Crossing:

```scripts/test_visual_crossing_request.py```

foto ilustrativa

Esse teste confirma que:

o ambiente virtual está funcionando;
o .env está sendo carregado;
a chave da Visual Crossing é válida;
a API está respondendo corretamente.

## 🧹 Qualidade de Código:

O projeto utiliza ruff para validação de estilo e identificação de problemas no código.

Durante o desenvolvimento, o ruff identificou um erro real de variável indefinida, o que reforça a importância de usar ferramentas de qualidade desde o início.

### 🧠 Boas Práticas Aplicadas:

### Engenharia de Dados:

- Separação entre camada raw e futuras camadas tratadas.
- Armazenamento do payload bruto da API.
- Uso de particionamento no S3.
- Inclusão futura de metadados de extração.
- Preparação para catálogo de dados com Glue.
- Estrutura compatível com consultas no Athena.

### Desenvolvimento:

- Ambiente isolado com Poetry.
- Dependências controladas por poetry.lock.
- Uso de .env para segredos locais.
- Uso de .env.example como documentação.
- Código validado com ruff.
- Separação entre script local e função Lambda.
- Versionamento com Git.

### Segurança:

- Chaves de API não são versionadas.
- Credenciais AWS não serão salvas no código.
- Lambda usará IAM Role para acessar o S3.
- Permissões IAM devem seguir o princípio do menor privilégio.

### 🗺️ Roadmap do Projeto
Próximas etapas planejadas:

- Criar a função lambda_function.py.
- Adaptar a requisição da Visual Crossing para execução na AWS Lambda.
- Gravar os dados brutos no Amazon S3.
- Criar particionamento por data, fonte e localização.
- Configurar variáveis de ambiente na Lambda.
- Configurar IAM Role com permissão mínima para S3.
- Agendar execução com Amazon EventBridge.
- Criar catálogo com AWS Glue Crawler.
- Consultar os dados com Amazon Athena.
- Criar camada tratada trusted/ ou silver/.
- Adicionar testes automatizados.
- Melhorar logs e monitoramento com CloudWatch.

### 📌 Status Atual:

Até o momento, o projeto possui:

- ambiente Poetry configurado;
- dependências instaladas;
- ambiente virtual ativado;
- script local consumindo a Visual Crossing API;
- variáveis de ambiente funcionando;
- validação com ruff;
