import random

import requests
from requests import Response


class Xkcd:
    api_url = "https://xkcd.com"
    info_filename = "info.0.json"

    def _get(self, path: str) -> Response:
        url = "/".join([self.api_url, path.lstrip("/")])
        return requests.get(url)

    def get_number(self, number: int) -> Response:
        return self._get("/".join([f"{number}", self.info_filename]))

    def get_latest(self) -> Response:
        return self._get(self.info_filename)

    def get_random(self) -> Response:
        response = self.get_latest()
        response.raise_for_status()

        latest_info = response.json()

        rand = random.randint(1, latest_info["num"])
        return self.get_number(rand)
