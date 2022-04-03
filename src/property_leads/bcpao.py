from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

import aiohttp


@dataclass
class BCPAOAccountInfo:
    account: int
    site_address: str
    parcel_id: str
    acreage: float
    zoning: str
    owners: str
    sale_date: Optional[date]
    sale_price: Optional[float]
    assessed_value: Optional[float]
    num_buildings: int
    base_area: Optional[int]
    sub_area: Optional[int]
    year_built: Optional[int]
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
            return [int(account_json["account"]) for account_json in await response.json()]

    async def get_account_info(self, account: int) -> BCPAOAccountInfo:
        account_url = self.ACCOUNT_URL_TEMPLATE.format(account=account)
        async with self.session.get(account_url, raise_for_status=True) as response:
            response_json = await response.json()

            sales_history = response_json.get("salesHistory") or [{}]
            sale_date_str = sales_history[0].get("saleDate")
            sale_date = datetime.fromisoformat(sale_date_str).date() if sale_date_str else None
            sale_price = sales_history[0].get("salePrice")
            value_summary = response_json.get("valueSummary") or [{}]
            assessed_value = value_summary[0].get("marketVal")
            buildings = response_json.get("buildings") or []

            num_buildings = 0
            year_built: List[int] = []
            base_area = None
            sub_area = None
            exterior_wall: List[str] = []
            frame: List[str] = []
            roof: List[str] = []
            roof_structure: List[str] = []
            has_pool = False
            has_fireplace = False
            for building in buildings:
                num_buildings += 1
                if building["totalBaseArea"]:
                    base_area = (base_area or 0) + building["totalBaseArea"]
                if building["totalSubArea"]:
                    sub_area = (sub_area or 0) + building["totalSubArea"]
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
            average_year_built = sum(year_built) // len(year_built) if year_built else None
            base_area = base_area or None
            sub_area = sub_area or None

            return BCPAOAccountInfo(
                account=int(response_json["account"]),
                site_address=response_json["siteAddress"],
                parcel_id=response_json["parcelID"],
                acreage=float(response_json["acreage"]),
                zoning=response_json["propertyUse"],
                owners=response_json["owner"],
                sale_date=sale_date,
                sale_price=sale_price,
                assessed_value=assessed_value,
                num_buildings=num_buildings,
                base_area=base_area,
                sub_area=sub_area,
                year_built=average_year_built,
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
