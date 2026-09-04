CREATE OR REPLACE VIEW tutor_analytics.v_tutor_events AS
WITH raw AS (
  SELECT
    timestamp AS log_timestamp,
    textPayload,
    REGEXP_EXTRACT(textPayload, r'tutor\.analytics\s*\|\s*(\{.*\})\s*$') AS json_str
  FROM tutor_analytics.run_googleapis_com_stderr
  WHERE textPayload LIKE '%tutor.analytics%'
    AND textPayload LIKE '%"event_type"%'
),
parsed AS (
  SELECT
    log_timestamp,
    JSON_VALUE(json_str, '$.event_type') AS event_type,
    SAFE.TIMESTAMP(JSON_VALUE(json_str, '$.timestamp')) AS event_timestamp,
    JSON_VALUE(json_str, '$.message_id') AS message_id,
    JSON_VALUE(json_str, '$.session_id') AS session_id,
    SAFE_CAST(JSON_VALUE(json_str, '$.user_id') AS INT64) AS user_id,
    JSON_VALUE(json_str, '$.display_name') AS display_name,
    SAFE_CAST(JSON_VALUE(json_str, '$.course_id') AS INT64) AS course_id,
    JSON_VALUE(json_str, '$.course_title') AS course_title,
    SAFE_CAST(JSON_VALUE(json_str, '$.post_id') AS INT64) AS post_id,
    JSON_VALUE(json_str, '$.post_type') AS post_type,
    JSON_VALUE(json_str, '$.post_title') AS post_title,
    SAFE_CAST(JSON_VALUE(json_str, '$.lesson_id') AS INT64) AS lesson_id,
    SAFE_CAST(JSON_VALUE(json_str, '$.topic_id') AS INT64) AS topic_id,
    SAFE_CAST(JSON_VALUE(json_str, '$.quiz_id') AS INT64) AS quiz_id,
    JSON_VALUE(json_str, '$.question') AS question,
    JSON_VALUE(json_str, '$.answer') AS answer,
    SAFE_CAST(JSON_VALUE(json_str, '$.feedback_score') AS INT64) AS feedback_score,
    SAFE_CAST(JSON_VALUE(json_str, '$.usage.input_tokens') AS INT64) AS input_tokens,
    SAFE_CAST(JSON_VALUE(json_str, '$.usage.output_tokens') AS INT64) AS output_tokens,
    SAFE_CAST(JSON_VALUE(json_str, '$.usage.total_tokens') AS INT64) AS total_tokens,
    SAFE_CAST(JSON_VALUE(json_str, '$.latency_ms') AS INT64) AS latency_ms,
    COALESCE(JSON_VALUE(json_str, '$.model'), 'default') AS model
  FROM raw
  WHERE json_str IS NOT NULL
)
SELECT
  p.*,
  (
    SAFE_DIVIDE(p.input_tokens, 1000000) * pr.input_usd_per_1m_tokens
    + SAFE_DIVIDE(p.output_tokens, 1000000) * pr.output_usd_per_1m_tokens
  ) AS cost_usd_estimado
FROM parsed p
LEFT JOIN tutor_analytics.model_pricing pr
  ON pr.model = COALESCE(p.model, 'default');
