import dataclasses
import inspect
import os
import random
from enum import Enum
from typing import List, Callable, Optional

import geonamescache
import requests
from imdb import Cinemagoer
from telegram import Update
from telegram.ext import ContextTypes

from .apininjas import ApiNinjas
from .thecatapi import TheCatApi
from .utils import escape_markdown, get_json_from_url, RequestError
from ..logger import create_logger


class MessageType(Enum):
    Text = "text"
    Photo = "photo"


def function_to_md(f: Callable):
    return escape_markdown(f.__name__.replace('action_', ''))


@dataclasses.dataclass
class Action:
    _f: Callable[[Update, ContextTypes], str]
    weight: float
    type: MessageType

    def __call__(self, *args, **kwargs):
        return self._f(*args, **kwargs)

    def name(self):
        return self._f.__name__

    def __str__(self):
        return f"{function_to_md(self._f)}: {self.weight} ({self.type.value})"


class TheDecider:
    actions: List[Action] = None

    def __init__(self):
        self.actions = []

    def add(self, weight: float = 10, message_type: MessageType = MessageType.Text):
        def wrapper(f: Callable[[Update, ContextTypes], str]):
            self.actions.append(Action(f, weight, message_type))

            return f

        return wrapper

    def find(self, name: str) -> Optional[Action]:
        for action in self.actions:
            action_name = action.name()
            if action_name == name.lower() or action_name == f"action_{name}".lower():
                return action

        return None

    def random(self) -> Action:
        return random.choices(
            [x for x in self.actions],
            weights=[x.weight for x in self.actions],
        )[0]

    def __str__(self):
        return "\n".join([str(action) for action in self.actions])


actions = TheDecider()


@actions.add(weight=10)
def action_random_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return escape_markdown(random.choice([
        "Hello World!",
        "This command is not supported",
    ]))


@actions.add(weight=10)
def action_official_joke_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)

    # https://github.com/15Dkatz/official_joke_api
    url = "https://official-joke-api.appspot.com/jokes/random"
    try:
        joke = get_json_from_url(url)
    except RequestError:
        log.exception("fail", exc_info=True)
        return

    setup = escape_markdown(joke["setup"])
    punchline = escape_markdown(joke["punchline"])
    return f"""{setup}

||{punchline}||"""


@actions.add(weight=5)
def action_apininjas_facts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = ApiNinjas("facts", {
        "limit": 1,
    })

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        return escape_markdown(res[0]["fact"])


@actions.add(weight=7)
def action_apininjas_chuck_norris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = ApiNinjas("chucknorris")

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        return escape_markdown(res["joke"])


@actions.add(weight=10)
def action_apininjas_dad_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = ApiNinjas("dadjokes", {
        "limit": 1,
    })

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        return escape_markdown(res[0]["joke"])


@actions.add(weight=4)
def action_apininjas_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = ApiNinjas("quotes", {
        "limit": 1,
    })

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        quote = escape_markdown(res[0]["quote"])
        author = escape_markdown(res[0]["author"])
        return fr""""{quote}"
\- _{author}_"""


@actions.add(weight=9)
def action_apininjas_trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = ApiNinjas("trivia", {
        "limit": 1,
    })

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))

    if res:
        question = escape_markdown(res[0]["question"])
        answer = escape_markdown(res[0]["answer"])
        return f"""{question}

||{answer}||"""


@actions.add(weight=8)
def action_apininjas_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = random.choice(list(geonamescache.GeonamesCache().get_cities().items()))[1]
    api = ApiNinjas("weather", {
        "lat": city['latitude'],
        "lon": city['longitude'],
    })

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))

    if res:
        temperature = escape_markdown(str(res["temp"]))
        city_name = escape_markdown(city["name"])
        country_name = escape_markdown(city["countrycode"])
        population = city["population"]
        timezone = escape_markdown(city["timezone"])
        return f"""It's {temperature}°C in {city_name}/{country_name}
Population: {population}
Timezone: {timezone}"""


@actions.add(weight=10)
def action_tim_imdb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = os.getenv("TIM_API_URL") or "https://api.timhatdiehandandermaus.consulting"
    url += "/movie?q="
    response = requests.get(url)
    js = response.json()

    info_types: list[str] = ["goofs", "trivia", "quotes"]
    api_movie = random.choice([movie for movie in js["movies"] if
                               movie["status"].lower() == "watched" or movie["imdb"]["title"] == "Airplane!"])
    c = Cinemagoer()
    imdb_movie = c.get_movie(api_movie["imdb"]["id"])
    c.update(imdb_movie, info_types)

    if not any(info_type in imdb_movie.data.keys() for info_type in info_types):
        return action_tim_imdb(update, context)

    random.shuffle(info_types)
    for info_type in info_types:
        try:
            info = random.choice(imdb_movie.data[info_type])
        except KeyError:
            continue
        if isinstance(info, dict):
            info_text = info["text"]
        elif isinstance(info, list):
            info_text = info[0]
        else:
            info_text = info

        info_text = escape_markdown(info_text)
        movie_text = escape_markdown(api_movie["imdb"]["title"])
        text = f"""||
{info_text}
||
\- {movie_text} \({info_type}\)
"""

    return text


@actions.add(weight=10, message_type=MessageType.Photo)
def action_apininjas_cats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MAX_OFFSET = 62  # experimentally checked that there are 82 available items and 20 items are returned by default
    random_offset = random.randint(0, MAX_OFFSET)
    api = ApiNinjas("cats", {
        "limit": 20,
        "min_weight": 1,  # arbitrary key since at least one filter has to be set
    })

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))

    if res:
        cat = random.choice(res)
        return cat["image_link"]

    return None


@actions.add(weight=10, message_type=MessageType.Photo)
def action_the_cat_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api = TheCatApi("v1/images/search", {})

    try:
        res = api.get()
    except RequestError as e:
        return escape_markdown("\n".join(e.args))

    if res:
        cat = random.choice(res)
        return cat["url"]

    return None
