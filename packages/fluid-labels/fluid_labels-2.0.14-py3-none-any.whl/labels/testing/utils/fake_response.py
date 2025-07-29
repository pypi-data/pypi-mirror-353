class MockResponse:
    def __init__(self, status_code: int, data: dict[object, object]) -> None:
        self.status_code = status_code
        self._data = data

    def json(self) -> dict[object, object]:
        return self._data
