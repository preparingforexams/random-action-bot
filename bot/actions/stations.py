import dataclasses
import unicodedata
from enum import Enum
from functools import lru_cache
from typing import Optional, Self

import requests
from bs4 import BeautifulSoup, Tag

from bot import actions


class StationType(Enum):
    BAHNHOF = "Bahnhof"
    HALTEPUNKT = "Haltepunkt"

    @classmethod
    def from_str(cls, s: str) -> Self:
        if s.lower() == "hp":
            return cls.HALTEPUNKT

        return cls.BAHNHOF

    def __str__(self):
        return self.value


class StopType(Enum):
    F = "Fernverkehrshalt"
    R = "Regionalverkehrshalt"
    S = "S-Bahn"

    @classmethod
    def from_columns(cls, c1: str, c2: str, c3: str):
        if len(c1) != 0:
            return cls.F
        elif len(c2) != 0:
            return cls.R

        return cls.S

    def __str__(self):
        return self.value


def format_routes(route_tag: Tag) -> str:
    routes = []
    for a in route_tag.find_all("a"):
        link = a['href']
        if not link.startswith("https://"):
            link = f"https://de.wikipedia.org{link}"
        if not link:
            link = " "
        routes.append(f"[{actions.escape_markdown(a.text)}]({actions.escape_markdown(link)})")

    return "\n".join(routes)


@dataclasses.dataclass
class Station:
    name: str
    name_link: str
    type: StationType
    tracks: Optional[int]
    town: str
    town_link: str
    district: str
    opening: str
    transport_association: str
    category: str
    stop_type: StopType
    route_tag: Tag
    notes: str
    _raw: str

    def __str__(self):
        return f"""
Name: [{actions.escape_markdown(self.name)}]({self.name_link})
Betriebsstelle: {actions.escape_markdown(str(self.type))}
Gleise: {self.tracks}
Stadt: [{actions.escape_markdown(self.town)}]({self.town_link})
Kreis: {actions.escape_markdown(self.district)}
Eröffnung: {actions.escape_markdown(self.opening)}
Verkehrsverbund: {actions.escape_markdown(self.transport_association)}
Kategorie: {actions.escape_markdown(self.category)}
Halt\-Typ: {actions.escape_markdown(str(self.stop_type))}
Strecke: {format_routes(self.route_tag)}
Anmerkungen: {actions.escape_markdown(self.notes)}"""


def get_link(t: Tag) -> str:
    a = t.find("a")
    if not a:
        return " "

    link = a["href"]
    if not link.startswith("https://"):
        link = f"https://de.wikipedia.org/{link}"

    return actions.escape_markdown(link)


@lru_cache()
def get_stations() -> Optional[list[Station]]:
    response = requests.get("https://de.wikipedia.org/wiki/Liste_der_Personenbahnh%C3%B6fe_in_Schleswig-Holstein")
    if not response.ok:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    out = soup.find_all("table")
    table = out[1]
    body = table.find("tbody")
    rows = body.find_all("tr")

    stations = []
    for row in rows[1:]:
        columns = row.find_all("td")
        tracks = int(unicodedata.normalize("NFKD", " ".join(columns[2].strings))) if " ".join(
            columns[2].strings) else None

        station = Station(
            unicodedata.normalize("NFKD", " ".join(columns[0].strings)),
            get_link(columns[0]),
            StationType.from_str(unicodedata.normalize("NFKD", " ".join(columns[1].strings))),
            tracks,
            unicodedata.normalize("NFKD", " ".join(columns[3].strings)),
            get_link(columns[3]),
            unicodedata.normalize("NFKD", " ".join(columns[4].strings)),
            unicodedata.normalize("NFKD", " ".join(columns[5].strings)),
            unicodedata.normalize("NFKD", " ".join(columns[6].strings)),
            unicodedata.normalize("NFKD", " ".join(columns[7].strings)),
            StopType.from_columns(unicodedata.normalize("NFKD", " ".join(columns[8].strings)),
                                  unicodedata.normalize("NFKD", " ".join(columns[9].strings)),
                                  unicodedata.normalize("NFKD", " ".join(columns[10].strings))),
            columns[11],
            unicodedata.normalize("NFKD", " ".join(columns[12].strings)).strip(),
            row
        )

        stations.append(station)

    return stations
