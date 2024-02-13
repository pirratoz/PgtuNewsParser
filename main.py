from asyncio import run as asyncio_run

from source.parser import NewsParser
from source.sql import DatabaseConnector


async def main() -> None:
    db = DatabaseConnector("database.db")
    db.create_tabel_news()

    parser = NewsParser()
    await parser.start_parse(db, simultaneous_requests=40)

    db.close_connection()


if __name__ == "__main__":
    asyncio_run(main())
