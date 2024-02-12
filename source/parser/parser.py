from bs4 import BeautifulSoup
from re import findall

from source.parser.query_builder import QueryBuilder
from source.parser.client import ClientSession
from source.parser.types import News


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
