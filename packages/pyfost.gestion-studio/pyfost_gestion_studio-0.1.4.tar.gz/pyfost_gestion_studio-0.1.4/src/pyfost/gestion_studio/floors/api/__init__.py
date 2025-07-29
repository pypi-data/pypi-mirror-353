import os
import httpx
from typing import Any

from uuid import UUID

from .models import Facility, Floor, Seat, Resource, Assignation, Task


class FloorsAPI:
    def __init__(self, host: str | None = None, port: int | None = None):
        host = host or os.environ["PYFOST__APPS__FLOORS__HOST"]
        port = port or int(os.environ["PYFOST__APPS__FLOORS__PORT"])
        url = f"http://{host}:{port}/api/floors/"

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
                f"API Error on {self._client.base_url}{endpoint} ({e.response.status_code}): {detail}"
            ) from e
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise Exception(f"Network or connection error: {e}") from e
        except Exception as e:
            print(f"Unexpected Error during API call: {e}")
            raise Exception(
                "An unexpected error occurred while contacting the API."
            ) from e

    async def get_facilities(self) -> list[Facility]:
        return [Facility(**i) for i in await self._request("GET", "facilities/")]

    async def get_facility_id(self, facility_name: str) -> UUID:
        return UUID(
            await self._request("GET", f"facilities/id_from_name/{facility_name}")
        )

    async def get_facility(self, facility_id: UUID) -> Facility:
        return Facility(**await self._request("GET", f"facilities/{facility_id}"))

    async def get_floors(self) -> list[Floor]:
        return [Floor(**i) for i in await self._request("GET", "floors/")]

    async def get_floor_id(self, facility_id: UUID, floor_name: str) -> UUID:
        params = {"facility_id": facility_id}
        return UUID(
            await self._request(
                "GET", f"floors/id_from_name/{floor_name}", params=params
            )
        )

    async def get_floor(self, floor_id: UUID) -> Floor:
        return Floor(**await self._request("GET", f"floors/{floor_id}"))

    async def set_floor_svg(self, floor_id: UUID, svg_path: str) -> Floor:
        # FIXME: absolutely untested and totaly human-vibe coded 😅
        files = {"file": open(svg_path, "rb")}
        data = await self._request("POST", f"floors/{floor_id}/svg", files=files)
        return Floor(**data)

    async def get_floor_svg(self, floor_id: UUID) -> Floor:
        return await self._request("GET", f"floors/{floor_id}/svg")

    async def get_seats(self) -> list[Seat]:
        return [Seat(**i) for i in await self._request("GET", "seats/")]

    async def get_resources(self) -> list[Resource]:
        return [Resource(**i) for i in await self._request("GET", "resources/")]

    async def get_assignations(self) -> list[Assignation]:
        return [Assignation(**i) for i in await self._request("GET", "assignations/")]

    async def get_tasks(self) -> list[Task]:
        return [Task(**i) for i in await self._request("GET", "tasks/")]

    async def get_task(self, task_id: UUID) -> Task:
        return Task(**await self._request("GET", f"tasks/{task_id}"))
