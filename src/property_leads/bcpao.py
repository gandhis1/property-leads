from dataclasses import dataclass
from datetime import date
from typing import List, Optional

import aiohttp
import pandas as pd


@dataclass
class BCPAOAccount:
    account: int
    site_address: str
    parcel_id: str
    acreage: int
    zoning: str
    owners: str
    sale_date: Optional[date]
    sale_price: Optional[float]
    assessed_value: Optional[float]
    num_buildings: int
    base_area: int
    sub_area: int
    year_built: int
    exterior_wall: Optional[str]
    frame: Optional[str]
    roof: Optional[str]
    roof_structure: Optional[str]
    has_pool: bool
    has_fireplace: bool


class BCPAODataFetcher:
    SEARCH_URL_TEMPLATE = "https://www.bcpao.us/api/v1/search?address={address}&activeonly=true&size={limit}&page=1"
    ACCOUNT_URL_TEMPLATE = "https://www.bcpao.us/api/v1/account/{account}"

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def find_matching_account(self, address: str) -> int:
        accounts = await self.find_matching_accounts(address)
        if len(accounts) == 0:
            raise NoAddressSearchResultsException(
                f"Could not find any accounts associated with the address '{address}'"
            )
        elif len(accounts) > 1:
            raise AmbiguousAddressSearchException(
                "Found multiple accounts associated with the address '{address}': {accounts}"
            )
        return accounts[0]

    async def find_matching_accounts(self, address: str, limit: int = 10) -> List[int]:
        search_url = self.SEARCH_URL_TEMPLATE.format(address=address, limit=limit)
        async with self.session.get(search_url, raise_for_status=True) as response:
            return [account_json["account"] for account_json in await response.json()]

    async def get_account_info(self, account: int) -> BCPAOAccount:
        account_url = self.ACCOUNT_URL_TEMPLATE.format(account=account)
        async with self.session.get(account_url, raise_for_status=True) as response:
            response_json = await response.json()

            sales_history = response_json.get("salesHistory", [{}])
            sale_date = pd.to_datetime(sales_history[0].get("saleDate")).date()
            sale_price = sales_history[0].get("salePrice")
            value_summary = response_json.get("valueSummary", [{}])
            assessed_value = value_summary[0].get("marketVal")

            num_buildings = 0
            year_built: List[int] = []
            base_area = 0
            sub_area = 0
            exterior_wall: List[str] = []
            frame: List[str] = []
            roof: List[str] = []
            roof_structure: List[str] = []
            has_pool = False
            has_fireplace = False
            for building in response_json["buildings"]:
                num_buildings += 1
                base_area += building["totalBaseArea"]
                sub_area += building["totalSubArea"]
                year_built.append(building["yearBuilt"])

                construction_info = building.get("constructionInfo", {})
                for ci in construction_info:
                    if ci["code"] == "EXTERIOR WALL":
                        exterior_wall.append(ci["description"])
                    elif ci["code"] == "FRAME":
                        frame.append(ci["description"])
                    elif ci["code"] == "ROOF":
                        roof.append(ci["description"])
                    elif ci["code"] == "ROOF STRUCTURE":
                        roof_structure.append(ci["description"])

                extra_feature_info = building.get("extraFeatureInfo", {})
                for efi in extra_feature_info:
                    if "POOL" in efi["description"]:
                        has_pool = True
                    elif "FIREPLACE" in efi["description"]:
                        has_fireplace = True

            return BCPAOAccount(
                account=response_json["account"],
                site_address=response_json["siteAddress"],
                parcel_id=response_json["parcelID"],
                acreage=response_json["acreage"],
                zoning=response_json["propertyUse"],
                owners=response_json["owner"],
                sale_date=sale_date,
                sale_price=sale_price,
                assessed_value=assessed_value,
                num_buildings=num_buildings,
                base_area=base_area,
                sub_area=sub_area,
                year_built=sum(year_built) / len(year_built),
                exterior_wall="/".join(exterior_wall) or None,
                frame="/".join(frame) or None,
                roof="/".join(roof) or None,
                roof_structure="/".join(roof_structure) or None,
                has_pool=has_pool,
                has_fireplace=has_fireplace,
            )


class AmbiguousAddressSearchException(RuntimeError):
    pass


class NoAddressSearchResultsException(RuntimeError):
    pass
