from typing import Any

from ..http import HttpClient
from ..schemas.asset_object import AssetObject


class Asset:
    __client: HttpClient

    def __init__(self, client: HttpClient):
        self.__client = client

    async def get_by_id(self, id: str) -> AssetObject | None:
        response = await self.__client.get(f'/asset/{id}')

        if response.is_error:
            return None

        return AssetObject(**response.json())

    async def query(self, query: dict[str, Any]) -> list[AssetObject]:
        response = await self.__client.post(f'/asset/query', json=query)

        return [AssetObject(**item) for item in response.json()]
