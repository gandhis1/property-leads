import asyncio

import aiohttp

from property_leads import BCPAODataFetcher

# TODO: Scrape Palm Bay permit web site "https://pay.palmbayflorida.org/Click2GovBP/index.html"
# TODO: Scrape property tax billing web site "https://brevard.county-taxes.com/public/real_estate/parcels/2836346"
# TODO: Scrape tax lien auction web site "https://www.brevard.realforeclose.com/index.cfm?zaction=USER&zmethod=CALENDAR"
# TODO: Write some unit tests
# TODO: Figure out how to properly version the wheel, including associating with Git tags


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        bcpao_data_fetcher = BCPAODataFetcher(session)
        account = await bcpao_data_fetcher.find_matching_account("1310 CHERRY HILLS RD NE PALM BAY FL 32905")
        account_info = await bcpao_data_fetcher.get_account_info(account)
        print(account_info)


if __name__ == "__main__":
    asyncio.run(main())
