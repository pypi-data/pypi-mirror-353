import asyncio
import json
import os
import time
import typing as t
import uuid

import httpx
import requests

from bespokelabs.curator.constants import BASE_CLIENT_URL, PUBLIC_CURATOR_VIEWER_DATASET_URL
from bespokelabs.curator.log import logger

N_CONCURRENT_VIEWER_REQUESTS = 100


class _SessionStatus:
    """A class to represent the status of a session."""

    STARTED = "STARTED"
    INPROGRESS = "INPROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Client:
    """A class to represent the client for the Curator Viewer."""

    def __init__(self, hosted: bool = False) -> None:
        """Initialize the client."""
        self._session = None
        self._state = None
        self._last_cost_projection_time = 0

        # Use environment variable to determine if hosted
        self._hosted = os.environ.get("CURATOR_VIEWER") in ["True", "true", "1", "t"]
        self._hosted = self._hosted or hosted
        self.semaphore = asyncio.Semaphore(N_CONCURRENT_VIEWER_REQUESTS)
        self._async_client = None
        self.api_key = os.environ.get("BESPOKE_API_KEY")
        if self.api_key:
            logger.info("Authenticated with Curator API key")
        self._headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    @property
    def session(self):
        """Get the session ID."""
        return self._session

    @property
    def authenticated(self):
        """Check if the client is authenticated."""
        return self._authenticated

    @property
    def hosted(self):
        """Check if the client is hosted."""
        return self._hosted

    @property
    def curator_viewer_url(self):
        """Get the curator viewer URL."""
        return f"{PUBLIC_CURATOR_VIEWER_DATASET_URL}/{self.session}" if self.session else None

    def create_session(self, metadata: t.Dict, session_id: str | None = None) -> str | None:
        """Sends a POST request to the server to create a session."""
        if not self.hosted:
            return str(uuid.uuid4().hex)

        if session_id:
            self._session = session_id
            return session_id
        if self.session:
            return self.session
        metadata.update({"status": _SessionStatus.STARTED})

        response = requests.post(f"{BASE_CLIENT_URL}/sessions", json=metadata, headers=self._headers)

        if response.status_code == 200:
            self._session = response.json().get("session_id")
            self._state = _SessionStatus.STARTED
            return self.session
        else:
            logger.warning(f"Failed to create session: {response.status_code}, {response.text}")
            return str(uuid.uuid4().hex)

    async def _update_state(self):
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{BASE_CLIENT_URL}/sessions/{self.session}", json={"status": self._state}, headers=self._headers)
        if response.status_code != 200:
            logger.debug(f"Failed to update session status: {response.status_code}, {response.text}")

    async def session_inprogress(self):
        """Updates the session status to inprogress."""
        self._state = _SessionStatus.INPROGRESS
        if not self._hosted and not self.session:
            return
        await self._update_state()

    async def session_completed(self):
        """Updates the session status to completed."""
        self._state = _SessionStatus.COMPLETED
        if not self._hosted and not self.session:
            return
        await self._update_state()

    async def session_failed(self):
        """Updates the session status to failed."""
        self._state = _SessionStatus.FAILED
        if not self._hosted and not self.session:
            return
        await self._update_state()

    async def stream_response(self, response_data: str, idx: int):
        """Streams the response data to the server."""
        if not self._hosted and not self.session:
            return
        if self._async_client is None:
            self._async_client = httpx.AsyncClient()

        response_data = json.dumps({"response_data": response_data})
        async with self.semaphore:
            response = await self._async_client.post(f"{BASE_CLIENT_URL}/sessions/{self.session}/responses/{idx}", data=response_data, headers=self._headers)

        if response.status_code != 200:
            logger.debug(f"Failed to stream response to curator Viewer: {response.status_code}, {response.text}")

    async def close(self):
        """Close the client."""
        if self._async_client:
            await self._async_client.aclose()

    async def log_cost_projection(self, status_tracker, force_log: bool = False):
        """Log the cost projection to the server."""
        if not self._hosted and not self.session:
            return
        # Track the last time we sent a cost projection
        current_time = time.time()

        if (current_time - self._last_cost_projection_time) < 10 and not force_log:
            return

        if self._async_client is None:
            self._async_client = httpx.AsyncClient()

        info = status_tracker.cost_info()

        async with self.semaphore:
            response = await self._async_client.put(f"{BASE_CLIENT_URL}/sessions/{self.session}", json=info, headers=self._headers)

        if response.status_code != 200:
            logger.debug(f"Failed to log cost projection: {response.status_code}, {response.text}")

        # Update the last projection time
        self._last_cost_projection_time = current_time
