import base64
import logging
from typing import Dict, Any

import requests

from app.core.config import settings


class ComplyCubeClient:
    def __init__(self):
        self.base_url = settings.complycube_base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": settings.complycube_api_key,
            "Content-Type": "application/json"
        })
        self.logger = logging.getLogger(__name__)

    def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/clients"
        self.logger.info(f"ComplyCube create_client -> POST {url}")
        try:
            resp = self.session.post(url, json=client_data)
            self.logger.info(f"ComplyCube create_client <- {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            body = None
            try:
                body = resp.text  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.error(
                f"ComplyCube create_client error: {getattr(exc, 'response', None) and exc.response.status_code}",
                extra={"url": url, "payload_keys": list(client_data.keys()), "response": body},
                exc_info=True,
            )
            raise

    def create_verification_session(self, client_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/clients/{client_id}/sessions"
        self.logger.info(f"ComplyCube create_session -> POST {url}")
        try:
            resp = self.session.post(url, json=session_data)
            self.logger.info(f"ComplyCube create_session <- {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            body = None
            try:
                body = resp.text  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.error(
                "ComplyCube create_session error",
                extra={"url": url, "client_id": client_id, "response": body},
                exc_info=True,
            )
            raise

    def get_client(self, client_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/clients/{client_id}"
        self.logger.info(f"ComplyCube get_client -> GET {url}")
        try:
            resp = self.session.get(url)
            self.logger.info(f"ComplyCube get_client <- {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            body = None
            try:
                body = resp.text  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.error(
                "ComplyCube get_client error",
                extra={"url": url, "client_id": client_id, "response": body},
                exc_info=True,
            )
            raise

    def get_verification_status(self, client_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/clients/{client_id}/verification"
        self.logger.info(f"ComplyCube get_verification_status -> GET {url}")
        try:
            resp = self.session.get(url)
            self.logger.info(f"ComplyCube get_verification_status <- {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            body = None
            try:
                body = resp.text  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.error(
                "ComplyCube get_verification_status error",
                extra={"url": url, "client_id": client_id, "response": body},
                exc_info=True,
            )
            raise

    def download_document(self, document_id: str, side: str = "front") -> Dict[str, Any]:
        url = f"{self.base_url}/documents/{document_id}/download/{side}"
        self.logger.info(f"ComplyCube download_document -> GET {url}")
        try:
            resp = self.session.get(url)
            self.logger.info(f"ComplyCube download_document <- {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            body = None
            try:
                body = resp.text  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.error(
                "ComplyCube download_document error",
                extra={"url": url, "document_id": document_id, "response": body},
                exc_info=True,
            )
            raise

    def list_documents(self, client_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/clients/{client_id}/documents"
        self.logger.info(f"ComplyCube list_documents -> GET {url}")
        try:
            resp = self.session.get(url)
            self.logger.info(f"ComplyCube list_documents <- {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            body = None
            try:
                body = resp.text  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.error(
                "ComplyCube list_documents error",
                extra={"url": url, "client_id": client_id, "response": body},
                exc_info=True,
            )
            raise


