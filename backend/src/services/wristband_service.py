import httpx
import logging
import os
from typing import Any, cast

logger = logging.getLogger(__name__)


class WristbandService:
    def __init__(self) -> None:
        application_vanity_domain = os.getenv("APPLICATION_VANITY_DOMAIN")
        if not application_vanity_domain:
            raise ValueError("wristband_application_vanity_domain required for WristbandApiClient")

        self._base_url: str = f"https://{application_vanity_domain}/api/v1"
        self._headers: dict[str, str] = {"Accept": "application/json", "Content-Type": "application/json"}
        self._client = httpx.AsyncClient()

    async def update_user_nickname(self, user_id: str, nickname: str, access_token: str) -> dict[str, Any]:
        # WRISTBAND_TOUCHPOINT: Update User API - https://docs.wristband.dev/reference/patchuserv1
        response: httpx.Response = await self._client.patch(
            self._base_url + f"/users/{user_id}",
            headers={**self._headers, "Authorization": f"Bearer {access_token}"},
            json={"nickname": nickname},
        )

        if response.status_code != 200:
            raise ValueError(f"Error calling update_user_nickname: {response.status_code} - {response.text}")

        return response.json() if response.content else {}

    async def get_user_nickname(self, user_id: str, access_token: str) -> str:
        # WRISTBAND_TOUCHPOINT: Get User API - https://docs.wristband.dev/reference/getuserv1
        response: httpx.Response = await self._client.get(
            self._base_url + f"/users/{user_id}", headers={**self._headers, "Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise ValueError(f"Error calling get_user_nickname: {response.status_code} - {response.text}")

        return cast(str, response.json().get("nickname", ""))
