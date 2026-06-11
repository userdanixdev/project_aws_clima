{{ config(
    materialized='view',
    schema='staging'
) }}

WITH base AS (

    SELECT *
    FROM {{ source('landing', 'clima') }}

),

renamed AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['location']) }} AS id_cidade,

        CAST(location_resolved AS VARCHAR) AS cidade,

        CAST(element.datetime AS DATE) AS data,

        CAST(element.temp AS DOUBLE) AS temperatura,
        CAST(element.tempmax AS DOUBLE) AS temperatura_max,
        CAST(element.tempmin AS DOUBLE) AS temperatura_min,

        CAST(element.feelslike AS DOUBLE) AS sensacao,
        CAST(element.feelslikemax AS DOUBLE) AS sensacao_max,
        CAST(element.feelslikemin AS DOUBLE) AS sensacao_min,

        CAST(element.humidity AS DOUBLE) AS umidade,

        CAST(element.precip AS DOUBLE) AS precipitacao,
        CAST(element.precipprob AS DOUBLE) AS prob_precipitacao,
        CAST(element.precipcover AS DOUBLE) AS area_precipitada,

        CAST(element.windgust AS DOUBLE) AS rajada_vento,
        CAST(element.windspeed AS DOUBLE) AS velocidade_vento,
        CAST(element.winddir AS DOUBLE) AS direcao_vento,

        CAST(element.uvindex AS INTEGER) AS indice_uv,

        CAST(element.cloudcover AS DOUBLE) AS cobertura_nuvens,
        CAST(element.visibility AS DOUBLE) AS visibilidade,

        CAST(element.sunrise AS VARCHAR) AS nascer_sol,
        CAST(element.sunset AS VARCHAR) AS por_sol,

        CAST(element.moonphase AS DOUBLE) AS fase_lua,

        CAST(element.conditions AS VARCHAR) AS condicao,
        CAST(element.description AS VARCHAR) AS descricao,

        CAST(element.source AS VARCHAR) AS fonte_dados,

        CASE
            WHEN element.source = 'comb'
                THEN 'obaservado'
            WHEN element.source = 'fcst'
                THEN 'previsao'
            ELSE 'desconhecido'
        END AS tipo_dado,

        CASE
            WHEN element.source = 'fcst'
                THEN TRUE
            ELSE FALSE
        END AS is_forecast,

                                                                              

        extraction_timestamp AS load_datetime

    FROM base b

    CROSS JOIN UNNEST(
        CAST(
            json_extract(
                json_parse(payload_json),
                '$.days'
            )
            AS ARRAY(
                ROW(
                    datetime VARCHAR,
                    temp DOUBLE,
                    tempmax DOUBLE,
                    tempmin DOUBLE,
                    feelslike DOUBLE,
                    feelslikemax DOUBLE,
                    feelslikemin DOUBLE,
                    humidity DOUBLE,
                    precip DOUBLE,
                    precipprob DOUBLE,
                    precipcover DOUBLE,
                    windgust DOUBLE,
                    windspeed DOUBLE,
                    winddir DOUBLE,
                    uvindex INTEGER,
                    cloudcover DOUBLE,
                    visibility DOUBLE,
                    sunrise VARCHAR,
                    sunset VARCHAR,
                    moonphase DOUBLE,
                    conditions VARCHAR,
                    description VARCHAR,
                    source VARCHAR
                )
            )
        )
    ) AS t(element)

)

SELECT *
FROM renamed