# Changelog

Todos los cambios notables de este Gateway serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]
### Added
- Documentación inicial estandarizada a nivel de repositorio.

## [0.1.0] - 2026-07-07
### Added
- Creación del Gateway como microservicio con FastAPI.
- Implementación de `agent_service.py` para llamar de forma asíncrona a Vertex AI Reasoning Engine.
- Endpoints implementados para recibir webhooks nativos:
  - `/webhook/telegram`
  - `/webhook/whatsapp`
  - `/api/chat` (Para testeo y uso web genérico)
- Configuración de Dockerfile optimizada para Google Cloud Run.
- Plantilla `.env.example` con la estructura de variables requerida por Google Cloud, Meta y Telegram.
