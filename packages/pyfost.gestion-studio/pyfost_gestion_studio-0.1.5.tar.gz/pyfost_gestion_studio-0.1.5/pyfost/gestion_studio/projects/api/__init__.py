import os
import httpx
from typing import Any

from .models import User, Project, Task


class ProjectsAPI:
    def __init__(self, host: str | None = None, port: int | None = None):
        host = host or os.environ["PYFOST__APPS__FLOORS__HOST"]
        port = port or int(os.environ["PYFOST__APPS__FLOORS__PORT"])
        url = f"http://{host}:{port}/api/projects/"

        self._client = httpx.AsyncClient(base_url=url, timeout=2.0)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Helper function to make requests and handle basic errors."""
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            if response.status_code == 204:  # No Content
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            # Try to get detail from response, otherwise use generic message
            detail = (
                e.response.json().get("detail", e.response.text)
                if e.response
                else str(e)
            )
            print(
                f"HTTP Error: {e.response.status_code} - {detail}"
            )  # Log detailed error
            raise Exception(
                f"API Error on {endpoint} ({e.response.status_code}): {detail}"
            ) from e
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise Exception(f"Network or connection error: {e}") from e
        except Exception as e:
            print(f"Unexpected Error during API call: {e}")
            raise Exception(
                "An unexpected error occurred while contacting the API."
            ) from e

    async def get_users(self) -> list[User]:
        return [User(**i) for i in await self._request("GET", "users/")]

    async def get_projects(self) -> list[Project]:
        return [Project(**i) for i in await self._request("GET", "projects/")]

    async def get_tasks(self) -> list[Task]:
        return [Task(**i) for i in await self._request("GET", "tasks/")]
