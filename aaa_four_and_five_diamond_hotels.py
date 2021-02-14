"""Convert the AAA four and five diamond hotel list from XML to JSON.

"""
import html
import json
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Address:
    """Mapping of the `address` XML element."""

    street_address: str
    city: str
    state: str
    postal_code: str
    country: str


@dataclass
class Hotel:
    """Mapping of the `travelItem` XML element."""

    id: int
    name: str
    rating: int
    address: Address


def extract() -> str:
    """Fetch hotel list from AAA website.

    Returns
    -------
    str
        Four and Five diamond hotels data as an XML document string.

    """
    url = "https://www.aaa.com/AAA/common/diamonds/xml/4-5-diamond-hotels.xml"
    with urllib.request.urlopen(url) as response:
        return response.read()


def transform(xml_data) -> List[Hotel]:
    """Parse XML AAA four and five diamond hotel data.

    Parameters
    ----------
    xml_data : str
        The output of the `extract()` function.

    Returns
    -------
    list of `Hotel`
        Sorted list of `Hotel` objects.

    """

    def _get_child(element: ET.Element, xpath: str, attr: str = None) -> Optional[str]:
        """Get a specific child element's attribute value.

        Defaults to element innertext if `attr` is `None`.

        Returns
        -------
        str or None
            The child element's selected attribute value if it exists.

        """
        child = element.find(xpath)
        if child is not None:
            return child.get(attr) if attr is not None else child.text

    def _parse_address(element: ET.Element) -> Address:
        """Traverse `travelItem` element tree to get address field data.

        Parameters
        ----------
        element : `ET.Element`
            A `travelItem` XML element.

        Returns
        -------
        `Address`
            The parsed `Address` object.

        """
        address_elem = element.find("./addresses/address[@type='PHYSICAL']")
        address = Address(
            street_address=_get_child(address_elem, "./addressLine"),
            city=_get_child(address_elem, "./cityName"),
            state=_get_child(address_elem, "./stateProv", attr="code"),
            postal_code=_get_child(address_elem, "./postalCode"),
            country=_get_child(address_elem, "./countryName"),
        )
        return address

    def _parse_hotel(element: ET.Element) -> Hotel:
        """Traverse `travelItem` element tree to get hotel field data.

        Parameters
        ----------
        element : ET.Element
            A `travelItem` XML element.

        Returns
        -------
        `Hotel`
            A  parsed `Hotel` object.

        """
        hotel = Hotel(
            id=element.get("id"),
            name=html.unescape(_get_child(element, "./itemName")),
            rating=_get_child(element, "./ratings/ratingCode"),
            address=_parse_address(element),
        )
        return hotel

    tree = ET.fromstring(xml_data)
    travel_items = tree.findall(".//travelItem")
    hotels = [_parse_hotel(travel_item) for travel_item in travel_items]
    hotels.sort(key=lambda x: x.id)
    return hotels


def load(records: List[Hotel]) -> bool:
    """Dump `Hotel` records into a JSON file.

    Parameters
    ----------
    records : list of Hotel
        The output of the `transform()` function.

    Returns
    -------
    bool
        Indicates whether data was written to disk  successfully.

    """
    output_filepath = (
        Path(__file__).parent.joinpath("aaa-four-and-five-diamond-hotels.json")
    )
    with open(output_filepath, "w") as f:
        records_dict = [asdict(record) for record in records]
        json.dump(records_dict, f, indent=4)


def main():
    """Main execution loop."""
    data = extract()
    hotels = transform(data)
    return load(hotels)


if __name__ == "__main__":
    main()
