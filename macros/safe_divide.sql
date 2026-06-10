{#
    Null-safe division. Returns NULL instead of erroring when the denominator is
    zero or NULL — used throughout the marts for rates and per-game averages.
#}
{% macro safe_divide(numerator, denominator) %}
    case
        when {{ denominator }} = 0 or {{ denominator }} is null then null
        else ({{ numerator }}) * 1.0 / ({{ denominator }})
    end
{% endmacro %}


{# Convenience wrapper: null-safe percentage (0-100). #}
{% macro pct(numerator, denominator) %}
    {{ safe_divide(numerator, denominator) }} * 100
{% endmacro %}
