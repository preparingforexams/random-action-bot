import os
from typing import Dict, List, Optional

from .utils import get_json_from_url


# https://api.nasa.gov/index.html
class NasaApi:
    base_url: str = "https://api.nasa.gov"

    def __init__(self, path: str, query_items: Dict = None):
        self.path = path.lstrip("/")
        self.query_items = query_items

    def assemble_url(self):
        url = f"{self.base_url}/{self.path}"
        if self.query_items:
            url += "?"
            url += "&".join([f"{key}={value}" for key, value in self.query_items.items()])

        return url

    def get(self) -> Optional[List | Dict]:
        self.query_items["api_key"] = os.getenv("NASA_API_KEY")
        url = self.assemble_url()

        return get_json_from_url(url)
