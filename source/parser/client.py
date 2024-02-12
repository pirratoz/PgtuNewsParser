from asyncio import sleep
import logging

from aiohttp import (
    ClientSession as AiohttpClientSession,
    ClientResponse,
)
from aiohttp.client_exceptions import ClientOSError

from source.parser.query_builder import RequestData


class ClientSession:
    def __init__(self) -> None:
        self.session: AiohttpClientSession | None = None
        self.__retry_send_request_sec: int = 4
    
    async def send(self, data: RequestData) -> ClientResponse:
        if self.session is None or self.session.closed:
            self.session = AiohttpClientSession()
        try:
            return await self.session.request(**data)
        except ClientOSError:
            logging.warning(f"ClientOSError, await {self.__retry_send_request_sec} sec.")
            await sleep(self.__retry_send_request_sec)
        
        return await self.send(data)

    async def close_session(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()
            await sleep(.25)
