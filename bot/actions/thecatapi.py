import os
from typing import Dict, List, Optional

from .utils import get_json_from_url


# https://developers.thecatapi.com/
class TheCatApi:
    base_url: str = "https://api.thecatapi.com"

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
        url = self.assemble_url()
        the_cats_api_key = os.getenv("THE_CATS_API_KEY")

        return get_json_from_url(url, headers={"X-Api-Key": the_cats_api_key})
