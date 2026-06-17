
-- CTE ( Common Table Expression ) -- 
WITH base AS (
    SELECT * FROM {{ref('int_clima_diario')}}
-- função do dbt para referenciar outro modelo 'intermediate' -- 
-- Assim cria dependência automática e permite construir uma DAG --     
    WHERE fonte_dados = 'comb'
-- Filtra apenas registros provenientes da fonte consolidade 'comb'
-- Para evitar dados de previsão forecast ('fcst')    
),

agregados AS (
    SELECT
        id_cidade,
        TRIM(cidade) AS cidade, -- TRIM -> remove espaços no início e fim to texto --
        date_trunc('month',data) AS mes, -- data para o primeiro dia do mês
-- para agrupar registros mensalmente -- 
        COUNT (*) AS dias_com_dados, -- Conta todos os registros de dias
-- Indicadores médios mensais --   
-- Temperaturas --      
        ROUND(AVG(temperatura),2) AS media_temperatura,
        MAX(temperatura_max) AS temperatura_max_mes,
        MIN(temperatura_min) AS temperatura_min_mes,
    -- Sensação térmica --
        ROUND(AVG(sensacao),2) AS media_sensacao,
    -- Umidade --                 
        ROUND(AVG(umidade),2) AS media_umidade,
    -- Chuva --         
        ROUND(AVG(precipitacao),2) AS media_precipitacao,
        ROUND(AVG(precipitacao_esperada),2) AS media_precipitacao_esperada,
        ROUND(SUM(CASE WHEN precipitacao > 0 THEN 1 ELSE 0 END),0) AS dias_com_chuva,
        -- Conta quantos dias do mês tiveram chuva -- 
        ROUND(AVG(amplitude_termica),2) AS media_amplitude_term,
        -- SOL // UV -- 
        ROUND(AVG(horas_sol),2) AS media_horas_sol,
        ROUND(AVG(indice_uv),2) AS media_uv,
        MAX(indice_uv) AS uv_max_mes,
        -- Vento --
        ROUND(AVG(velocidade_vento),2) AS velo_media_vento,
        MAX(rajada_vento) AS rajada_max_mes,
        -- Atmosfera -- 
        ROUND(AVG(cobertura_nuvens),2) AS media_cobertura_nuvens,
        ROUND(AVG(visibilidade),2) AS media_visibilidade,
        -- ALERTAS --
        SUM (
            CASE 
                WHEN alerta_uv THEN 1
                ELSE 0
            END
        ) AS dias_alerta_uv,
        SUM(
            CASE
                WHEN alerta_vento THEN 1
                ELSE 0
            END                
        ) AS dias_alerta_vento             
            
       
    FROM base
    GROUP BY id_cidade, TRIM(cidade), date_trunc('month', data)        
),
-- Determinação da condição climática mais frequente -- 

frequencia_condicao AS (
    SELECT
        id_cidade,
        date_trunc('month',data) AS mes,
        condicao,
        COUNT(*) AS ocorrencias,
-- Conta quantas vezes cada condição climática apareceu --         
        ROW_NUMBER() OVER (
            PARTITION BY id_cidade, date_trunc('month',data) 
-- Window Function: Cria uma numeração nova para cada linha dentro de um grupo (cidade e mês)        
        ORDER BY COUNT(*)DESC) AS ordem -- Ordena da mais frequente para a menos -- 
    FROM base
    GROUP BY
        id_cidade,
        date_trunc('month',data),
        condicao        
),
-- Coluna com a condição climática que mais aparece em que retona o primeiro colocado -- 
condicao_mais_comum AS (
    SELECT id_cidade, mes, condicao AS condicao_mais_frequente
    FROM frequencia_condicao
    WHERE ordem = 1
),
-- Determinação da Fase da Lua Mais Comum --
-- Mesma lógica para a condição climática --
frequencia_lua AS (
    SELECT 
        id_cidade,
        date_trunc('month',data) AS mes,
        fase_lua_nome,
        COUNT(*) AS ocorrencias,
        ROW_NUMBER()OVER (PARTITION BY id_cidade,date_trunc('month',data) ORDER BY COUNT(*)DESC) AS ordem
    FROM base
    GROUP BY id_cidade, date_trunc('month',data), fase_lua_nome
),    

lua_mais_comum AS (
    SELECT id_cidade, mes, fase_lua_nome AS lua_mais_comum
    FROM frequencia_lua
    WHERE ordem = 1
),

-- Determinação de tempertura mais frequente --

frequencia_faixa_temperatura AS (
    SELECT
        id_cidade,
        date_trunc('month', data) AS mes,
        faixa_temperatura,
        COUNT(*) AS ocorrencias,
        ROW_NUMBER()OVER(
            PARTITION BY
                id_cidade,
                date_trunc('month',data)
            ORDER BY COUNT(*) DESC                    
        ) AS ordem
    FROM base
    GROUP BY 
        id_cidade,
        date_trunc('month',data),
        faixa_temperatura        
),
temperatura_predominante AS (
    SELECT
        id_cidade,
        mes,
        faixa_temperatura AS faixa_temperatura_predominante
    FROM frequencia_faixa_temperatura
    WHERE ordem = 1       
),
frequencia_faixa_uv AS (
    SELECT
        id_cidade,
        date_trunc('month',data) AS mes,
        faixa_uv,
        COUNT(*) AS ocorrencias,
        ROW_NUMBER() OVER(
            PARTITION BY
                id_cidade,
                date_trunc('month',data)
            ORDER BY COUNT(*) DESC                
        ) AS ordem
    FROM base
    GROUP BY
        id_cidade,
        date_trunc('month',data),
        faixa_uv        
    ),
    uv_predominante AS (
        SELECT
            id_cidade,
            mes,
            faixa_uv AS faixa_uv_predominante
        FROM frequencia_faixa_uv
        WHERE ordem = 1            
    )
SELECT
    a.*,
    c.condicao_mais_frequente,
    l.lua_mais_comum,
    t.faixa_temperatura_predominante,
    u.faixa_uv_predominante
FROM agregados a    
LEFT JOIN condicao_mais_comum c ON a.id_cidade = c.id_cidade AND a.mes = c.mes
LEFT JOIN lua_mais_comum l ON a.id_cidade = l.id_cidade AND a.mes = l.mes
LEFT JOIN temperatura_predominante t ON a.id_cidade = t.id_cidade AND a.mes = t.mes
LEFT JOIN uv_predominante u ON a.id_cidade = u.id_cidade AND a.mes = u.mes

-- A camada Mart responde perguntas como:

-- Qual foi a temperatura máxima do mês?
-- Qual cidade teve mais chuva?
-- Quantos dias tiveram alerta UV?
-- Qual foi a condição climática predominante?
-- O mês foi predominantemente "Quente" ou "Muito Quente"?
-- Qual foi a classificação UV predominante?
-- Qual cidade apresentou maior score climático?


