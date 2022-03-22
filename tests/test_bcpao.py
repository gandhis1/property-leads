import aiohttp
import pytest_asyncio
from typing import Any

from property_leads import BCPAODataFetcher


class TestBCPAODataFetcher:
    @pytest_asyncio.fixture
    async def mock_bcpao_data_fetcher(self, monkeypatch: Any) -> BCPAODataFetcher:
        async with aiohttp.ClientSession() as client_session:
            monkeypatch.setattr(client_session, "get", None)
            yield BCPAODataFetcher(client_session)

    async def test_find_matching_account(self, mock_bcpao_data_fetcher: BCPAODataFetcher) -> None:
        assert True  # TODO

    async def test_find_matching_accounts(self, mock_bcpao_data_fetcher: BCPAODataFetcher) -> None:
        assert True  # TODO

    async def test_get_account_info(self, mock_bcpao_data_fetcher: BCPAODataFetcher) -> None:
        assert True  # TODO
