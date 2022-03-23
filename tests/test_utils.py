import json
from contextlib import AbstractAsyncContextManager
from typing import Any, Dict


class MockAioHttpClient:
    def __init__(self, request_url_to_json_response: Dict[str, str]):
        self.request_url_to_json_response = request_url_to_json_response

    def get(self, url: str, *args, **kwargs):
        return MockAioHttpClientResponse(self.request_url_to_json_response[url])


class MockAioHttpClientResponse(AbstractAsyncContextManager):
    def __init__(self, json_str: str):
        self.json_str = json_str

    async def json(self) -> Dict[str, Any]:
        return json.loads(self.json_str)

    async def __aexit__(self, *args, **kwargs) -> None:
        pass
