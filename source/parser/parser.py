from asyncio import gather as asyncio_gather
from math import ceil
from typing import (
    Coroutine,
    Callable,
)
from re import findall

from bs4 import BeautifulSoup

from source.parser.query_builder import QueryBuilder
from source.sql.connector import DatabaseConnector
from source.parser.client import ClientSession
from source.parser.types import News


class UtilsParser:
    @staticmethod
    def create_tasks(
        start_page: int,
        simultaneous_requests: int,
        func: Callable
    ) -> list[Coroutine]:
        return [
            func(page)
            for page in range(start_page, start_page + simultaneous_requests)
        ]

    @staticmethod
    def convert_results_for_insert(results: list[list[News]]) -> list[tuple[str, str]]:
        return [
            (news.title, f"http://www.penzgtu.ru/{news.url}")
            for result in results
            for news in result
        ]


class NewsParser:
    def __init__(self) -> None:
        self.__session = ClientSession()
        self.__query_builder = QueryBuilder()

    async def close_session(self) -> None:
        await self.__session.close_session()

    async def get_count_news(self) -> int:
        response_data = await self.__session.send(
            self.__query_builder.get_news_page(None)
        )
        soup = BeautifulSoup(await response_data.text(), "html.parser")
        result = soup.find(attrs={"class": "showResultsWrap"})
        if result:
            return int(findall(r"\d+", result.text)[2])
        return 0

    async def get_count_news_on_page(self) -> int:
        response_data = await self.__session.send(
            self.__query_builder.get_news_page(None)
        )
        soup = BeautifulSoup(await response_data.text(), "html.parser")
        result = soup.find_all(attrs={"class": "news_list_wrapper"})
        if result:
            return len(result)
        return 0

    async def get_news_from_page(self, page_number: int) -> list[News]:
        news = []
        response_data = await self.__session.send(
            self.__query_builder.get_news_page(page_number)
        )
        soup = BeautifulSoup(await response_data.text(), "html.parser")
        finded_news = soup.find_all(attrs={"class": "news_list_wrapper"})
        for _news in finded_news:
            result = _news.find(name="a")
            if result:
                news.append(News(title=result["title"], url=result["href"]))
        return news

    async def start_parse(
        self,
        db: DatabaseConnector,
        simultaneous_requests: int = 40
    ) -> None:
        
        count_news = await self.get_count_news()
        count_news_on_page = await self.get_count_news_on_page()
        count_pages = ceil(count_news / count_news_on_page)

        for start_page in range(0, count_pages, simultaneous_requests):
            news: list[tuple[str, str]] = UtilsParser.convert_results_for_insert(
                await asyncio_gather(
                    *UtilsParser.create_tasks(start_page, simultaneous_requests, self.get_news_from_page)
                )
            )
            db.insert_news(news)
            print(f"Pages = {start_page + simultaneous_requests} / {count_pages} | news = {len(news)}")
            db.connection.commit()

        await self.close_session()
