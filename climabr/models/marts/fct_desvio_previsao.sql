

WITH base AS (
    SELECT * FROM {{ref('int_clima_diario')}}

),
-- Coluna apenas com atributos necessários para análise e calculos de desvio entre previsão e realizado
separado AS (
    SELECT
        cidade,
        data,

        temperatura,
        sensacao,
        umidade,
        precipitacao,

        indice_uv,
        velocidade_vento,
        visibilidade,
        cobertura_nuvens,

        amplitude_termica,
        horas_sol,
        precipitacao_esperada,

        fonte_dados

    FROM base        
    WHERE fonte_dados IN ('fcst','comb')
-- Condicional que mantém somente os registros de previsão 'fcst' e consolidados 'comb'    
),
-- Transforma os registros em colunas para permitir a comparação direta
-- Utiliza a agregação MAX apenas para pivotar os valores

pivotado AS (
    SELECT
        cidade,
        data,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN temperatura END) AS temperatura_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN temperatura END) AS temperatura_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN sensacao END) AS sensacao_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN sensacao END) AS sensacao_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN umidade END) AS umidade_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN umidade END) AS umidade_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN precipitacao END) AS precipitacao_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN precipitacao END) AS precipitacao_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN indice_uv END) AS indice_uv_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN indice_uv END) AS indice_uv_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN velocidade_vento END) AS velocidade_vento_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN velocidade_vento END) AS velocidade_vento_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN visibilidade END) AS visibilidade_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN visibilidade END) AS visibilidade_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN cobertura_nuvens END) AS cobertura_nuvens_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN cobertura_nuvens END) AS cobertura_nuvens_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN amplitude_termica END) AS amplitude_termica_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN amplitude_termica END) AS amplitude_termica_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN horas_sol END) AS horas_sol_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN horas_sol END) AS horas_sol_comb,

        MAX(CASE WHEN fonte_dados = 'fcst' THEN precipitacao_esperada END) AS precipitacao_esperada_fcst,
        MAX(CASE WHEN fonte_dados = 'comb' THEN precipitacao_esperada END) AS precipitacao_esperada_comb

    FROM separado
    GROUP BY
        cidade,
        data
),
-- Calcula o erro de previsão para cada métrica -- 
desvios AS (
    SELECT
        cidade,
        data,
        ROUND(temperatura_fcst - temperatura_comb, 2) AS desvio_temperatura,
        ROUND(sensacao_fcst - sensacao_comb, 2) AS desvio_sensacao, 
        ROUND(umidade_fcst - umidade_comb, 2) AS desvio_umidade,
        ROUND(precipitacao_esperada_fcst - precipitacao_esperada_comb, 2) AS desvio_precipitacao_esperada, 
        ROUND(indice_uv_fcst - indice_uv_comb, 2) AS desvio_uv,
        ROUND(velocidade_vento_fcst  - velocidade_vento_comb, 2) AS desvio_velocidade_vento,
        ROUND(visibilidade_fcst - visibilidade_comb, 2) AS desvio_visibilidade,
        ROUND(cobertura_nuvens_fcst - cobertura_nuvens_comb, 2) AS desvio_cobertura_nuvens, 
        ROUND(amplitude_termica_fcst - amplitude_termica_comb, 2) AS desvio_amplitude_termica, 
        ROUND(horas_sol_fcst - horas_sol_comb, 2) AS desvio_horas_sol
        
    FROM pivotado

    WHERE temperatura_fcst IS NOT NULL AND temperatura_comb IS NOT NULL        
    )
    SELECT * FROM desvios

    -- Assim, cada linha por cidade e data contendo todos os desvios entre previsão e realizado --

-- Agora a fato passa a responder perguntas como:

-- Quanto a previsão errou na temperatura?
-- Quanto errou na sensação térmica?
-- Quanto errou na precipitação?
-- Quanto errou no índice UV?
-- Quanto errou na cobertura de nuvens?
-- Quanto errou nas horas de sol?
-- Quanto errou na visibilidade?


