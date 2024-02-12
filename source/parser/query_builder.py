from typing import (
    TypedDict,
    Literal,
    Any,
)


class RequestData(TypedDict):
    method: Literal["GET", "POST"]
    url: str
    params: dict[str, Any] | None
    json: dict[str, Any] | None


class QueryBuilder:
    def __init__(self) -> None:
        pass
    
    def get_news_page(self, page: int | None = None) -> RequestData:
        return RequestData(
            method="GET",
            url="http://www.penzgtu.ru/272/273/browse/" + (f"{page}/" if page else ""),
            params=None,
            json=None
        )
