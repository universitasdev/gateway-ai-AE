# Tutor Analytics 360 — Fase 4 (BigQuery)

Proyecto GCP: `chatbot-academy-wp`  
Servicio Cloud Run: `academy-ae-gateway` (us-east1)

## Recursos

| Tipo | Nombre |
|------|--------|
| Dataset | `tutor_analytics` |
| Sink Logging | `tutor-analytics-to-bq` |
| Tabla raw | `run_googleapis_com_stderr` (particionada por `timestamp`) |
| Precios | `model_pricing` |
| Vista | `v_tutor_events` |
| Vista | `v_tutor_auditoria` |

## Filtro del sink

```
resource.type="cloud_run_revision"
AND resource.labels.service_name="academy-ae-gateway"
AND textPayload:"tutor.analytics"
```

Writer SA: `service-919237484930@gcp-sa-logging.iam.gserviceaccount.com` (WRITER en el dataset).

## Consultas útiles

```sql
-- Conteos por tipo
SELECT event_type, COUNT(*) AS n
FROM `chatbot-academy-wp.tutor_analytics.v_tutor_events`
GROUP BY 1;

-- Auditoría reciente
SELECT *
FROM `chatbot-academy-wp.tutor_analytics.v_tutor_auditoria`
ORDER BY event_timestamp DESC
LIMIT 50;
```

## FinOps

`cost_usd_estimado` se calcula en la vista con `model_pricing`.  
Actualizar filas en `model_pricing` cuando se confirmen tarifas del modelo (no en el BFF).

## Limitación

El sink no importa logs anteriores a su creación. Tras crear el sink, generar al menos un chat y un feedback nuevos para validar.
