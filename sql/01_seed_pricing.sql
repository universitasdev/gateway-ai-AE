INSERT INTO tutor_analytics.model_pricing
  (model, input_usd_per_1m_tokens, output_usd_per_1m_tokens, effective_from, notes)
SELECT * FROM UNNEST([
  STRUCT(
    'default' AS model,
    0.10 AS input_usd_per_1m_tokens,
    0.40 AS output_usd_per_1m_tokens,
    DATE '2026-01-01' AS effective_from,
    'Placeholder: actualizar tarifas Vertex del agente' AS notes
  )
])
WHERE NOT EXISTS (
  SELECT 1 FROM tutor_analytics.model_pricing p WHERE p.model = 'default'
);
