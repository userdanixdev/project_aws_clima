{% macro classify_moon_phase(moonphase_value) %}
    CASE
        WHEN {{ moonphase_value }} = 0 THEN 'Lua Nova'
        WHEN {{ moonphase_value }} > 0 AND {{ moonphase_value }} < 0.25 THEN 'Crescente Côncava'
        WHEN {{ moonphase_value }} = 0.25 THEN 'Quarto Crescente'
        WHEN {{ moonphase_value }} > 0.25 AND {{ moonphase_value }} < 0.5 THEN 'Gibosa Crescente'
        WHEN {{ moonphase_value }} = 0.5 THEN 'Lua Cheia'
        WHEN {{ moonphase_value }} > 0.5 AND {{ moonphase_value }} < 0.75 THEN 'Gibosa Minguante'
        WHEN {{ moonphase_value }} = 0.75 THEN 'Quarto Minguante'
        WHEN {{ moonphase_value }} > 0.75 AND {{ moonphase_value }} <= 1 THEN 'Crescente Minguante'
        ELSE 'Fase Desconhecida'
    END
{% endmacro %}