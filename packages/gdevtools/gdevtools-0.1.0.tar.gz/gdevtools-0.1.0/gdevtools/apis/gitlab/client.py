from contextlib import asynccontextmanager
import httpx
from pydantic import HttpUrl
import os

from typing import AsyncGenerator


class GitLabApiClientManager:
    def __init__(self, url: HttpUrl = HttpUrl("https://gitlab.com")) -> None:
        self.url: HttpUrl = HttpUrl(str(url) + "api/v4")
        self.token: str = self._get_gitlab_token()

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[httpx.Client, None]:
        async with self._client() as client:
            yield client

    ####################
    # Helper functions #
    ####################

    def _client(self, headers: dict[str, str] | None = None) -> httpx.AsyncClient:
        if headers is None:
            headers = {}

        return httpx.AsyncClient(
            base_url=str(self.url), headers={**{"PRIVATE-TOKEN": self.token}, **headers}
        )

    @staticmethod
    def _get_gitlab_token(env_var: str = "GITLAB_TOKEN") -> str:
        """
        Fetches a gitlab token from an environment variable.
        """
        token: str | None = os.environ.get(env_var)
        if token is None:
            raise ValueError(
                f"Environment variable '{env_var}' is not set. Please set it to have permissions to access gitlab."
            )
        return token
