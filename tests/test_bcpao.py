import functools
import math

import pytest
from test_utils import MockAioHttpClient

from property_leads import (
    AmbiguousAddressSearchException,
    BCPAODataFetcher,
    NoAddressSearchResultsException,
)


class TestBCPAODataFetcher:
    async def test_find_matching_account(self, monkeypatch: pytest.MonkeyPatch) -> None:
        bcpao_data_fetcher = BCPAODataFetcher(None)

        monkeypatch.setattr(
            bcpao_data_fetcher, "find_matching_accounts", functools.partial(self.mock_find_matching_accounts, [1])
        )
        assert await bcpao_data_fetcher.find_matching_account("address") == 1, "Expected only account 1 to be returned"

        monkeypatch.setattr(
            bcpao_data_fetcher, "find_matching_accounts", functools.partial(self.mock_find_matching_accounts, [])
        )
        with pytest.raises(NoAddressSearchResultsException):
            await bcpao_data_fetcher.find_matching_account("address")

        monkeypatch.setattr(
            bcpao_data_fetcher, "find_matching_accounts", functools.partial(self.mock_find_matching_accounts, [1, 2])
        )
        with pytest.raises(AmbiguousAddressSearchException):
            await bcpao_data_fetcher.find_matching_account("address")

    @staticmethod
    async def mock_find_matching_accounts(return_value, *args, **kwargs):
        return return_value

    async def test_find_matching_accounts(self) -> None:
        ADDRESS_INPUT = "200 BABCOCK ST"
        MATCH_LIMIT = 2
        REQUEST_URL = (
            f"https://www.bcpao.us/api/v1/search?address={ADDRESS_INPUT}&activeonly=true&size={MATCH_LIMIT}&page=1"
        )
        JSON_RESPONSE = """
        [
            {
                "totalCount": 2,
                "searchType": "R",
                "propertyID": 2728703,
                "account": "2728703",
                "parcelID": "27-37-28-75-*-18",
                "siteAddress": "200 S BABCOCK ST MELBOURNE FL 32901",
                "subdivisionName": "NIEMAN HEIGHTS",
                "landUseCode": "OFFICE BUILDING - SINGLE TENANT - 1 STORY         ",
                "taxingDistrict": "MELBOURNE",
                "totalBaseArea": 1400,
                "totalSubArea": 1482,
                "acreage": 0.34,
                "saleDate": "2016-09-25T00:00:00",
                "salePrice": 195000.0,
                "officialBook": "7992",
                "officialPage": "0414",
                "mailAddress": "200 S BABCOCK ST MELBOURNE FL 32901",
                "mailFormatted1": "BOLTZ, BRADFORD",
                "mailFormatted2": "BOLTZ, TAMMY",
                "mailFormatted3": "200 S BABCOCK ST",
                "mailFormatted4": "MELBOURNE FL 32901-1210",
                "mailFormatted5": null,
                "owners": "BOLTZ, BRADFORD; BOLTZ, TAMMY",
                "condoNumber": null,
                "condoName": null,
                "businessName": null,
                "businessSiteAddress": null,
                "businessMailAddress": null,
                "businessLicense": null,
                "yearBuilt": "1957",
                "poolFlag": false,
                "inactiveFlag": false,
                "masterPhotoUrl": "https://www.bcpao.us/photos/27/27287030110.jpg",
                "marketValue": 152050.0,
                "saleInfo": "09/25/2016 $195,000 Improved"
            },
            {
                "totalCount": 2,
                "searchType": "R",
                "propertyID": 2819382,
                "account": "2819382",
                "parcelID": "28-37-04-75-A",
                "siteAddress": "2004 S BABCOCK ST UNIT PARK MELBOURNE FL 32901",
                "subdivisionName": "COUNTRY CLUB COLONY",
                "landUseCode": "MUNICIPALLY OWNED LAND - VACANT  ",
                "taxingDistrict": "MELBOURNE",
                "totalBaseArea": 0,
                "totalSubArea": 0,
                "acreage": 0.25,
                "saleDate": null,
                "salePrice": null,
                "officialBook": null,
                "officialPage": null,
                "mailAddress": "ATTN: CITY MANAGER 900 E STRAWBRIDGE AVE MELBOURNE FL 32901",
                "mailFormatted1": "MELBOURNE, CITY OF",
                "mailFormatted2": "ATTN: CITY MANAGER",
                "mailFormatted3": "900 E STRAWBRIDGE AVE",
                "mailFormatted4": "MELBOURNE FL 32901",
                "mailFormatted5": null,
                "owners": "MELBOURNE, CITY OF",
                "condoNumber": null,
                "condoName": null,
                "businessName": null,
                "businessSiteAddress": null,
                "businessMailAddress": null,
                "businessLicense": null,
                "yearBuilt": "        ",
                "poolFlag": false,
                "inactiveFlag": false,
                "masterPhotoUrl": null,
                "marketValue": 1150.0,
                "saleInfo": "--"
            }
        ]
        """

        mock_client = MockAioHttpClient({REQUEST_URL: JSON_RESPONSE})
        bcpao_data_fetcher = BCPAODataFetcher(mock_client)

        accounts = await bcpao_data_fetcher.find_matching_accounts(ADDRESS_INPUT, MATCH_LIMIT)
        assert len(accounts) == 2, f"Expected two accounts returned associated with the search input '{ADDRESS_INPUT}'"
        assert accounts[0] == 2728703, "Expected the first account returned to be account 2728703"
        assert accounts[1] == 2819382, "Expected the second account returned to be account 2819382"

    async def test_get_account_info(self) -> None:
        ACCOUNT_INPUT = 2819382
        REQUEST_URL = f"https://www.bcpao.us/api/v1/account/{ACCOUNT_INPUT}"
        JSON_RESPONSE = """
        {
            "lastModifiedDate": "3/23/2022 3:35:00 AM",
            "account": "2819382",
            "nextAccount": 2819383,
            "prevAccount": 2819381,
            "parcelID": "28-37-04-75-A",
            "parcelTownship": "28",
            "parcelRange": "37",
            "parcelSection": "04",
            "parcelSubdivision": "75",
            "parcelBlock": "A",
            "parcelLot": "",
            "siteAddress": "2004 S BABCOCK ST UNIT PARK MELBOURNE FL 32901",
            "subdivisionName": "COUNTRY CLUB COLONY",
            "owner": "MELBOURNE, CITY OF",
            "masterPhotoUrl": null,
            "sketchUrl": "",
            "platBook": null,
            "platPage": null,
            "platBookPage": "0004/0017",
            "legalDescription": "COUNTRY CLUB COLONY 2 UNNUMBERED LOTS N & E OF LOTS 8 TO 16, SOUTH OF NEW HAVEN AVE & WEST OF BABCOCK ST EX RD R/W",
            "acreage": 0.25,
            "totalBuildings": 0,
            "rollYear": 2021,
            "marketValue": "$1,150",
            "saleInfo": "--",
            "mailFormatted1": "MELBOURNE, CITY OF",
            "mailFormatted2": "ATTN: CITY MANAGER",
            "mailFormatted3": "900 E STRAWBRIDGE AVE",
            "mailFormatted4": "MELBOURNE FL 32901",
            "mailFormatted5": null,
            "mailingAddress": {
                "addr1": "ATTN: CITY MANAGER",
                "addr2": "900 E STRAWBRIDGE AVE",
                "city": "MELBOURNE",
                "state": "FL",
                "zip": "32901",
                "country": "",
                "formatted": "ATTN: CITY MANAGER 900 E STRAWBRIDGE AVE MELBOURNE FL  32901",
                "isForeign": false
            },
            "propertyUse": {
                "code": "8080",
                "description": "MUNICIPALLY OWNED LAND - VACANT"
            },
            "siteCode": {
                "code": "0320",
                "description": "BABCOCK"
            },
            "millage": {
                "code": "34K0",
                "description": "MELBOURNE"
            },
            "marketArea": {
                "code": "510000",
                "description": null
            },
            "redevelopmentZone": null,
            "ownerNames": [
                {
                    "ownerName": "MELBOURNE, CITY OF",
                    "ownerSequence": "1",
                    "primaryOwner": true
                }
            ],
            "siteAddresses": [
                {
                    "siteAddress": "2004 S BABCOCK ST UNIT PARK MELBOURNE FL 32901",
                    "locationSequence": "1",
                    "isPrimaryFlag": true
                }
            ],
            "exemptions": [
                {
                    "code": "EXMU",
                    "description": "MUNICIPALLY OWNED PROPERTY"
                }
            ],
            "valueSummary": [
                {
                    "sequence": null,
                    "rollYear": 2021,
                    "marketVal": 1150.0,
                    "agriculturalVal": 0.0,
                    "assessedValSch": 1150.0,
                    "assessedVal": 1150.0,
                    "homesteadEx": 0.0,
                    "addlHomesteadEx": 0.0,
                    "otherExempts": 1150,
                    "taxableValSch": 0.0,
                    "taxableVal": 0.0,
                    "marketVal1": 1150.0,
                    "agriculturalVal1": 0.0,
                    "assessedValSch1": 1150.0,
                    "assessedVal1": 1150.0,
                    "homesteadEx1": 0.0,
                    "addlHomesteadEx1": 0.0,
                    "otherExempts1": 1150,
                    "taxableValSch1": 0.0,
                    "taxableVal1": 0.0,
                    "marketVal2": 1150.0,
                    "agriculturalVal2": 0.0,
                    "assessedValSch2": 1150.0,
                    "assessedVal2": 1150.0,
                    "homesteadEx2": 0.0,
                    "addlHomesteadEx2": 0.0,
                    "otherExempts2": 1150,
                    "taxableValSch2": 0.0,
                    "taxableVal2": 0.0
                }
            ],
            "salesHistory": null,
            "landInfo": [
                {
                    "acreage": "0.25",
                    "legalDesc": "COUNTRY CLUB COLONY 2 UNNUMBERED LOTS N & E OF LOTS 8 TO 16, SOUTH OF NEW HAVEN AVE & WEST OF BABCOCK ST EX RD R/W",
                    "platBookPage": "0004/0017",
                    "subdivisionName": "COUNTRY CLUB COLONY",
                    "siteCode": {
                        "code": "0320",
                        "description": "BABCOCK"
                    }
                }
            ],
            "addlXFeatures": [],
            "buildings": null,
            "condoInfo": null,
            "tangibleInfo": null,
            "isCondo": false,
            "condoNumber": 0,
            "condoFirstAccount": null,
            "isConfidential": false,
            "noData": false,
            "isInactive": false
        }
        """

        mock_client = MockAioHttpClient({REQUEST_URL: JSON_RESPONSE})
        bcpao_data_fetcher = BCPAODataFetcher(mock_client)

        account_info = await bcpao_data_fetcher.get_account_info(ACCOUNT_INPUT)
        assert account_info.account == ACCOUNT_INPUT, f"Expected info to be associated with account '{ACCOUNT_INPUT}'"
        assert account_info.site_address == "2004 S BABCOCK ST UNIT PARK MELBOURNE FL 32901"
        assert account_info.owners == "MELBOURNE, CITY OF"
        assert account_info.num_buildings == 0
        assert math.isclose(account_info.acreage, 0.25)
        assert math.isclose(account_info.assessed_value, 1150.0)
