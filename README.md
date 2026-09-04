# Gateway Actas de Entrega — Vertex AI Agent Runtime

## Título y Descripción
El **Gateway Actas de Entrega** es un microservicio (BFF - Backend For Frontend) que sirve como puente de comunicación ("Orejas y Boca") entre múltiples canales externos (Web, WhatsApp, Telegram) y el cerebro del sistema: el Agente de IA alojado en Google Cloud Vertex AI (Reasoning Engine).

Este proyecto resuelve el problema de integración, recibiendo webhooks, estandarizando los mensajes de los usuarios y gestionando las sesiones (`session_id`) antes de pasarlas de forma segura al agente alojado en la nube. No contiene lógica de IA ni de negocio, es puramente un orquestador de APIs de mensajería.

## Relación con el Agente Actas de Entrega
Este proyecto funciona en conjunto con el repositorio del **Agente Actas de Entrega**:
- El **Agente** (Reasoning Engine) es el "cerebro". Entiende el contexto y consulta el Data Store (RAG).
- El **Gateway** (este repositorio) es la interfaz pública en Cloud Run. Toma los eventos de Telegram/WhatsApp, se autentica con GCP, llama al Agente pasándole el ID de la sesión del chat, y cuando el agente responde, el Gateway se encarga de formatear el JSON para mandarle el mensaje de vuelta al teléfono del usuario.

## Prerrequisitos
- **Python 3.11+**
- **Docker** (para empaquetado y despliegue)
- **Google Cloud CLI** (`gcloud`) para autenticación.
- Cuentas de desarrollador y Tokens de acceso para la API de Telegram y Meta Cloud API (WhatsApp).

## Instalación y Configuración

Sigue estos pasos para levantar el entorno en tu máquina local:

1. **Clonar el repositorio y entrar al directorio:**
   ```bash
   git clone <url-del-repo>
   cd gateway-ai-ae
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   Copia la plantilla y edita con tus credenciales reales.
   ```bash
   cp .env.example .env
   ```

4. **Autenticación con Google Cloud (Application Default Credentials):**
   ```bash
   gcloud auth application-default login
   ```

## Scripts Principales

A continuación se listan los comandos más utilizados para operar el proyecto:

- **Levantar el servidor local (Desarrollo):**
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```
- **Probar el estado (Health Check):**
  ```bash
  curl http://localhost:8000/health
  ```
- **Probar el endpoint web (Simulación de Chat):**
  ```bash
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hola, ¿qué puedes hacer?", "session_id": "test-123"}'
  ```
  Respuesta incluye `message_id` (UUID) y opcionalmente `usage` (tokens).  
  Feedback: `POST /api/feedback` con `{ "message_id", "session_id", "feedback_score": 1|-1 }`.
- **Construir y desplegar a Cloud Run directamente:**
  ```bash
  gcloud run deploy gateway --source . --region us-central1 --allow-unauthenticated
  ```

---

## Estructura del Proyecto

```
gateway/
├── app/
│   ├── main.py                  # Entry point + lifespan
│   ├── core/
│   │   └── config.py            # Settings (.env)
│   ├── services/
│   │   └── agent_service.py     # Wrapper ReasoningEngine
│   ├── api/v1/
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── web.py           # POST /api/chat
│   │       ├── telegram.py      # POST /webhook/telegram
│   │       └── whatsapp.py      # GET+POST /webhook/whatsapp
│   └── schemas/
│       └── messages.py          # Pydantic models
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

## Configuración de Webhooks en Producción

Una vez desplegado en Cloud Run, obtendrás una URL como `https://gateway-xxxxx.run.app`.

### Telegram
Para que Telegram envíe los mensajes de los usuarios a tu Gateway, registra el webhook:
```bash
curl "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://gateway-xxxxx.run.app/webhook/telegram"
```

### WhatsApp
1. Ve al [Meta App Dashboard](https://developers.facebook.com/)
2. En **Webhooks**, configura la URL: `https://gateway-xxxxx.run.app/webhook/whatsapp`
3. Usa el mismo `WHATSAPP_VERIFY_TOKEN` que configuraste en tu `.env`
4. Suscríbete al campo `messages`

## Permisos requeridos
La Service Account asociada al servicio de Cloud Run necesita contar con el rol `roles/aiplatform.user` en IAM para poder ejecutar las consultas contra el Vertex AI Reasoning Engine alojado en el otro proyecto.
