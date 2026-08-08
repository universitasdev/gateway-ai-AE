# Documentación y Plan de Construcción: Gateway GIRS (Agent Runtime)

Este documento sirve como base de conocimiento y guía de implementación para el desarrollo de un Gateway (BFF) en Cloud Run. Este Gateway conectará un Agente de IA desplegado en Google Cloud Vertex AI (Agent Runtime) con múltiples canales de comunicación (Web, WhatsApp y Telegram).

---

## 1. Contexto de la Arquitectura
*   **El Cerebro (Agent Runtime):** El agente de IA ha sido desarrollado con el framework ADK (`agents-cli`) y reside en la infraestructura serverless de Vertex AI. Su gestión de estado (sesiones) es manejada automáticamente por el `VertexAiSessionService`. Su función única es recibir texto y devolver texto.
*   **Las Orejas/Boca (Cloud Run Gateway):** Un servicio web ligero, independiente, cuyo único propósito es procesar webhooks externos, estandarizar los mensajes entrantes, llamar al agente en Vertex AI y reestructurar la respuesta para enviarla de vuelta a la plataforma original.

---

## 2. Requisitos Técnicos del Gateway
*   **Infraestructura:** Google Cloud Run.
*   **Autenticación hacia el Agente:** Uso del SDK `google-cloud-aiplatform` con una Service Account que tenga el rol `roles/aiplatform.user`.
*   **Endpoints requeridos:**
    *   `POST /webhook/telegram`: Recibe y parsea eventos de la API de Telegram.
    *   `POST /webhook/whatsapp`: Recibe y parsea eventos de la API de WhatsApp Business (o Twilio).
    *   `POST /api/chat`: Endpoint genérico para la web (recibe `{ "message": "...", "session_id": "..." }`).
*   **Gestión de Memoria (TTL):** Implementar lógica para limpiar sesiones antiguas si un usuario solicita reiniciar la conversación.

---

## 3. Plan de Implementación Paso a Paso

### Fase 1: Inicialización del Proyecto
1.  Crear un nuevo repositorio/carpeta separada.
2.  Inicializar un proyecto en Node.js (Express/NestJS) o Python (FastAPI). *(Recomendación: FastAPI en Python para mantener sinergia con el ecosistema de IA de Google).*
3.  Instalar dependencias clave: Servidor web, SDK de Google Cloud (`google-cloud-aiplatform`), cliente HTTP para enviar mensajes.

### Fase 2: Configuración del SDK de Vertex AI
1.  Crear una clase o servicio `AgentService` que inicialice la conexión con GCP.
2.  Implementar la función central que recibe el mensaje limpio y el `session_id`, llama a `ReasoningEngine(AGENT_ID).query(input=..., config={"session_id": ...})`, y retorna el texto de la IA.

### Fase 3: Integración de Canales (Webhooks)
1.  **Endpoint Web:** Un controlador REST simple que pasa los datos al `AgentService`.
2.  **Endpoint Telegram:** Implementar la validación de Telegram, extraer el `chat.id` (como `session_id`) y el `text`. Responder haciendo una petición HTTP a la API oficial de Telegram con la respuesta del agente.
3.  **Endpoint WhatsApp:** Implementar la validación del Token (`hub.challenge`), parsear el JSON anidado para extraer el teléfono del remitente y el mensaje. Responder usando la Graph API de Meta.

### Fase 4: Despliegue en Cloud Run
1.  Escribir el `Dockerfile`.
2.  Desplegar en Cloud Run con la bandera `--allow-unauthenticated` para que los webhooks sean accesibles públicamente.
3.  Configurar la URL pública resultante en los paneles de control de Telegram (BotFather) y Meta (WhatsApp Developer Portal).

---

> [!IMPORTANT]
> **Copia el siguiente prompt y pégalo en una nueva sesión / proyecto vacío de Antigravity IDE para que el agente te construya el Gateway completo.**

## 4. Prompt Maestro para Antigravity IDE

```text
¡Hola! Necesito que actúes como un Ingeniero Backend Experto en Google Cloud y APIs de mensajería.

Quiero construir un "Gateway GIRS" para conectar mis plataformas con un Agente de IA que ya tengo desplegado en Vertex AI Reasoning Engine (Agent Runtime). Este Gateway debe ser un microservicio independiente, construido en Python usando FastAPI, y diseñado para ser desplegado en Google Cloud Run.

El flujo de trabajo es el siguiente:
1. El usuario envía un mensaje por WhatsApp, Telegram o Web.
2. El Gateway recibe el webhook de la plataforma correspondiente.
3. El Gateway limpia el mensaje, y usa el SDK `google-cloud-aiplatform` para enviar la consulta al Reasoning Engine. El `session_id` que se enviará al agente debe ser el número de teléfono (en WhatsApp) o el Chat ID (en Telegram).
4. Al recibir la respuesta del Reasoning Engine, el Gateway le hace una petición HTTP a la API de WhatsApp o Telegram para enviarle el texto al usuario.

Requisitos del entregable:
1. Genera la estructura del proyecto (archivos `.py`, `requirements.txt`, `Dockerfile`).
2. Crea el archivo de configuración `.env.example` donde pondremos el `PROJECT_ID`, `LOCATION`, `REASONING_ENGINE_ID`, y los tokens de Telegram/WhatsApp.
3. Implementa los 3 endpoints (`/webhook/telegram`, `/webhook/whatsapp`, `/api/web`) usando buenas prácticas y separando la lógica de la llamada a Vertex AI en un archivo `agent_service.py`.
4. Incluye instrucciones para probarlo localmente y los comandos para desplegar el contenedor a Cloud Run permitiendo tráfico no autenticado.

Usa la documentación oficial de `google-cloud-aiplatform` para llamar a la clase `ReasoningEngine`. ¡Adelante!
```
