"""
Service layer that wraps the Vertex AI Reasoning Engine / Agent Engine API.

Centralises all interaction with the deployed AI agent so that
endpoint code never touches the SDK directly.
"""

import json
import logging
from typing import Any, Optional

import google.auth
from google.auth.transport.requests import Request
import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self):
        settings = get_settings()
        self._project_id = settings.project_id
        self._location = settings.location
        self._engine_id = settings.reasoning_engine_id

        self._credentials, _ = google.auth.default()
        self._base = (
            f"https://{self._location}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{self._project_id}/locations/{self._location}/"
            f"reasoningEngines/{self._engine_id}"
        )
        self._query_endpoint = f"{self._base}:query"
        self._stream_endpoint = f"{self._base}:streamQuery"

    def init(self):
        """No complex initialization needed for REST client."""
        logger.info(
            f"Initialized AgentService pointing to Reasoning Engine: "
            f"{self._engine_id} at {self._location}"
        )

    def _headers(self) -> dict:
        if not self._credentials.valid:
            self._credentials.refresh(Request())
        return {
            "Authorization": f"Bearer {self._credentials.token}",
            "Content-Type": "application/json",
        }

    def _post_query(self, class_method: str, input_payload: dict) -> Any:
        """Call AdkApp methods exposed on the :query endpoint."""
        response = requests.post(
            self._query_endpoint,
            headers=self._headers(),
            json={"classMethod": class_method, "input": input_payload},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        self._raise_if_error_payload(data)
        return data

    @staticmethod
    def _extract_session_id(data: Any) -> Optional[str]:
        if isinstance(data, str) and data:
            return data.rsplit("/", 1)[-1]
        if not isinstance(data, dict):
            return None
        for key in ("id", "session_id", "sessionId"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value.rsplit("/", 1)[-1]
        name = data.get("name")
        if isinstance(name, str) and name:
            return name.rsplit("/", 1)[-1]
        output = data.get("output")
        if output is not None:
            return AgentService._extract_session_id(output)
        return None

    def _resolve_vertex_session(self, user_id: str) -> str:
        """Reuse or create a session via AdkApp async_* methods on :query.

        Must use the same session store that async_stream_query reads;
        the raw Sessions REST API IDs are not always visible to ADK.
        """
        try:
            listed = self._post_query("async_list_sessions", {"user_id": user_id})
            sessions: list = []
            if isinstance(listed, dict):
                if isinstance(listed.get("sessions"), list):
                    sessions = listed["sessions"]
                elif isinstance(listed.get("output"), dict):
                    sessions = listed["output"].get("sessions") or []
                elif isinstance(listed.get("output"), list):
                    sessions = listed["output"]
            if sessions:
                existing = self._extract_session_id(sessions[0])
                if existing:
                    logger.info(f"Reusing ADK session {existing} for user {user_id}")
                    return existing
        except Exception as e:
            logger.warning(f"async_list_sessions failed, will async_create_session: {e}")

        created = self._post_query("async_create_session", {"user_id": user_id})
        session_id = self._extract_session_id(created)
        if not session_id:
            raise RuntimeError(f"async_create_session no devolvió id: {created}")
        logger.info(f"Created ADK session {session_id} for user {user_id}")
        return session_id

    @staticmethod
    def _raise_if_error_payload(data: Any) -> None:
        """streamQuery often returns HTTP 200 with an embedded error object."""
        if not isinstance(data, dict):
            return
        code = data.get("code")
        message = data.get("message") or data.get("error_message")
        if code and message and "content" not in data and "output" not in data:
            raise RuntimeError(f"Agent Engine error {code}: {message}")

    def _parse_stream_response(self, response: requests.Response) -> str:
        """Parse NDJSON / SSE chunks from :streamQuery into plain text."""
        text = response.text.strip()
        if not text:
            return ""

        # Single JSON object (error or non-streamed payload)
        if text.startswith("{"):
            try:
                data = json.loads(text)
                self._raise_if_error_payload(data)
                if isinstance(data, dict):
                    if "output" in data:
                        return str(data["output"])
                    if "text" in data:
                        return str(data["text"])
                    if "content" in data and "parts" in data.get("content", {}):
                        parts = data["content"]["parts"]
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
            except json.JSONDecodeError:
                pass

        full_response = ""
        for line in text.splitlines():
            if line.startswith("data:"):
                line = line[5:].strip()
            if not line or line == "[DONE]":
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                full_response += line
                continue

            if not isinstance(data, dict):
                full_response += str(data)
                continue

            self._raise_if_error_payload(data)

            if "output" in data:
                full_response += str(data["output"])
            elif "text" in data:
                full_response += data["text"]
            elif "content" in data and "parts" in data.get("content", {}):
                parts = data["content"]["parts"]
                if parts and "text" in parts[0]:
                    full_response += parts[0]["text"]

        return full_response

    def query_agent(self, prompt: str, session_id: Optional[str] = None) -> str:
        """Query the ADK Agent Engine via :streamQuery (async_stream_query)."""
        try:
            user_id = session_id or "default-user"
            vertex_session_id = self._resolve_vertex_session(user_id)

            payload = {
                "classMethod": "async_stream_query",
                "input": {
                    "user_id": user_id,
                    "session_id": vertex_session_id,
                    "message": prompt,
                },
            }

            logger.info(
                f"Sending streamQuery for user={user_id} session={vertex_session_id}"
            )
            response = requests.post(
                self._stream_endpoint,
                headers=self._headers(),
                json=payload,
                timeout=120,
            )
            response.raise_for_status()

            full_response = self._parse_stream_response(response)
            if not full_response:
                return "El agente no devolvió ninguna respuesta (vacío)."
            return full_response

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Error querying agent: {str(e)}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise RuntimeError(f"Error de conexión con el Agente: {str(e)}")
        except Exception as e:
            logger.error(f"Error consulting agent: {str(e)}")
            raise RuntimeError(f"Error consultando al agente: {str(e)}")


_agent_service = AgentService()


def init() -> None:
    _agent_service.init()


def query_agent(message: str, session_id: str) -> str:
    """Module-level wrapper for query_agent."""
    return _agent_service.query_agent(message, session_id)
