from httpx import Response

from ..http import HttpClient


class Status:
    __client: HttpClient

    def __init__(self, client: HttpClient):
        self.__client = client

    async def health(self) -> Response:
        return await self.__client.get(f'/health')

    async def info(self) -> Response:
        return await self.__client.get(f'/info')
