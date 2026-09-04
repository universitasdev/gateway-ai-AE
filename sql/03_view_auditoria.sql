CREATE OR REPLACE VIEW tutor_analytics.v_tutor_auditoria AS
SELECT
  c.event_timestamp,
  c.user_id,
  c.display_name,
  c.course_id,
  c.post_id,
  c.post_title,
  c.lesson_id,
  c.question,
  c.answer,
  c.message_id,
  c.session_id,
  c.input_tokens,
  c.output_tokens,
  c.cost_usd_estimado,
  c.latency_ms,
  f.feedback_score,
  f.event_timestamp AS feedback_timestamp
FROM tutor_analytics.v_tutor_events c
LEFT JOIN tutor_analytics.v_tutor_events f
  ON f.event_type = 'feedback'
 AND f.message_id = c.message_id
WHERE c.event_type = 'chat';
