# Changelog

Todos los cambios notables de este Gateway serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]
### Added
- **Tutor Analytics 360 (Fase 2):** `user_context` opcional en `/api/chat`, `message_id` + `usage` en la respuesta, logs JSON estructurados (`tutor.analytics`), endpoint `POST /api/feedback`.
- El BFF **no** calcula dólares; solo reporta tokens cuando Vertex los expone.

### Changed
- `agent_service.query_agent` ahora devuelve `AgentReply(text, usage)` (Telegram/WhatsApp usan `.text`).

## [0.1.0] - 2026-07-07
### Added
- Documentación inicial estandarizada a nivel de repositorio.
- Creación del Gateway como microservicio con FastAPI.
- Implementación de `agent_service.py` para llamar de forma asíncrona a Vertex AI Reasoning Engine.
- Endpoints implementados para recibir webhooks nativos:
  - `/webhook/telegram`
  - `/webhook/whatsapp`
  - `/api/chat` (Para testeo y uso web genérico)
- Configuración de Dockerfile optimizada para Google Cloud Run.
- Plantilla `.env.example` con la estructura de variables requerida por Google Cloud, Meta y Telegram.
