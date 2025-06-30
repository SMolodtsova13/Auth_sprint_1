from fastapi import Query


class PaginationParams:
    def __init__(
        self,
        page_number: int = Query(
            1, ge=1, description='Номер страницы'
        ),
        page_size: int = Query(
            50,
            ge=1,
            le=100,
            description='Количество записей на странице'
        ),
    ):
        self.page_number = page_number
        self.page_size = page_size
