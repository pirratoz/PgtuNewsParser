from asyncio import gather as asyncio_gather
from asyncio import run as asyncio_run
from math import ceil
from typing import (
    Coroutine,
    Callable,
)

from source.parser.types import News
from source.parser import NewsParser
from source.sql import DatabaseConnector


def create_tasks(
    start_page: int,
    simultaneous_requests: int,
    func: Callable
) -> list[Coroutine]:
    return [
        func(page)
        for page in range(start_page, start_page + simultaneous_requests)
    ]


def convert_results_for_insert(results: list[list[News]]) -> list[tuple[str, str]]:
    return [
        (news.title, f"http://www.penzgtu.ru/{news.url}")
        for result in results
        for news in result
    ]


async def handle_tasks(tasks: list[Coroutine]) -> list[list[News]]:
    return await asyncio_gather(*tasks)


async def start_parse(
    db: DatabaseConnector,
    simultaneous_requests: int = 40
) -> None:
    
    parser = NewsParser()

    count_news = await parser.get_count_news()
    count_news_on_page = await parser.get_count_news_on_page()
    count_pages = ceil(count_news / count_news_on_page)

    for start_page in range(0, count_pages, simultaneous_requests):
        news = await handle_tasks(
            tasks=create_tasks(start_page, simultaneous_requests, parser.get_news_from_page)
        )
        news = convert_results_for_insert(news)
        db.insert_news(news)
        print(f"Pages = {start_page + simultaneous_requests} / {count_pages} | news = {len(news)}")
        db.connection.commit()

    await parser.close_session()


async def main() -> None:
    simultaneous_requests = 40
    db = DatabaseConnector("database.db")
    db.create_tabel_news()

    await start_parse(db, simultaneous_requests)

    db.close_connection()


if __name__ == "__main__":
    asyncio_run(main())
