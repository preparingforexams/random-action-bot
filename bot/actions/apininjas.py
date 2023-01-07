import os
from typing import Dict, List, Optional

from .utils import get_json_from_url


class ApiNinjas:
    base_url: str = "https://api.api-ninjas.com/v1"

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
        api_ninjas_key = os.getenv("API_NINJAS_KEY")

        return get_json_from_url(url, headers={"X-Api-Key": api_ninjas_key})
