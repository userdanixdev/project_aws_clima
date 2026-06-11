{{ config(materialized='view',schema='intermediate')}}

WITH base AS(
    SELECT *
    FROM {{ref('stg_clima')}}
),

enriched AS(
    SELECT
        --CHAVES:
        id_cidade,
        -- Dimensões:
        cidade,
        data,
        fonte_dados,
        -- Temperatura:
        temperatura,
        temperatura_max,
        temperatura_min,
        -- Sensação térmica:
        sensacao,
        sensacao_max,
        sensacao_min,
        -- Umidade e precipitação>
        umidade,
        precipitacao,
        prob_precipitacao,
        area_precipitada,
        -- vento:
        velocidade_vento,
        rajada_vento,
        direcao_vento,
        -- Atmosfera:
        indice_uv,
        cobertura_nuvens,
        visibilidade,
        -- Astronomia:
        nascer_sol,
        por_sol,
        fase_lua,
        {{classify_moon_phase('fase_lua')}} AS fase_lua_nome,
        -- condições climáticas --
        condicao,
        descricao,
        -- Métricas derivadas --
        ROUND(temperatura_max - temperatura_min,2) AS amplitude_termica,
        ROUND(precipitacao * (prob_precipitacao/100),2) AS precipitacao_esperada,
        ROUND(
            date_diff(
                'minute',
                CAST(nascer_sol AS time),
                CAST(por_sol AS time)
            ) / 60.0,
            2
        ) AS horas_sol,

        -- Classificações das temperaturas -- 
        CASE 
            WHEN temperatura < 15 THEN 'Frio'                    
            WHEN temperatura < 25 THEN 'Ameno'                                    
            WHEN temperatura < 30 THEN 'Quente'
            ELSE 'Muito Quente'
        END AS faixa_temperatura,            

        -- Classificações Ultra Violeta (UV) -- 

        CASE 
            WHEN indice_uv <= 2 THEN 'Baixo'
            WHEN indice_uv <= 5 THEN 'Moderado'
            WHEN indice_uv <= 7 THEN 'Alto'
            WHEN indice_uv <= 10 THEN 'Muito Alto'
            ELSE 'Extremo'
        END AS faixa_uv,

        -- Classificação de Umidade -- 
        CASE 
            WHEN velocidade_vento < 10 THEN 'Fraco'            
            WHEN velocidade_vento < 30 THEN 'Moderado'
            WHEN velocidade_vento < 30 THEN 'Forte'
            ELSE 'Muito Forte'
        END AS faixa_vento,

        -- Classificação de visibilidade -- 
        CASE
            WHEN visibilidade >= 10 THEN 'Excelente'
            WHEN visibilidade >= 5 THEN 'Boa'
            WHEN visibilidade >= 2 THEN 'Moderada'                                    
            ELSE 'Baixa'
        END AS faixa_visibilidade,

        -- Indicadores booleanos --
        CASE
            WHEN precipitacao > 0 THEN TRUE
            ELSE FALSE
        END AS houve_chuva,

        CASE
            WHEN prob_precipitacao >= 70 THEN TRUE
            ELSE FALSE
        END AS alta_prob_chuva,

        CASE
            WHEN indice_uv >= 8 THEN TRUE
            ELSE FALSE
        END AS alerta_uv,

        CASE 
            WHEN temperatura_max >= 35 THEN TRUE
            ELSE FALSE
        END AS alerta_calor,

        CASE
            WHEN rajada_vento >= 50 THEN TRUE
            ELSE FALSE
        END AS alerta_vento,

        -- Score Climático Simples --
        ROUND (
            ( COALESCE(temperatura,0)
            + COALESCE(indice_uv,0)
            + COALESCE(velocidade_vento,0)
            ),2) AS score_climatico,
        load_datetime            
    FROM base
    )
    SELECT * FROM enriched
                                                                                            


        

    
