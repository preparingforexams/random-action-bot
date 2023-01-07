import inspect
import os
import random
import socket
from typing import Dict, Optional

import requests
import urllib3 as urllib3
from telegram import Update
from telegram.ext import ContextTypes

from ..logger import create_logger


def escape_markdown(text: str) -> str:
    reserved_characters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for reserved in reserved_characters:
        text = text.replace(reserved, fr"\{reserved}")

    return text


class RequestError(Exception):
    pass


def get_json_from_url(url: str, *, headers: Dict = None) -> Optional[Dict]:
    log = create_logger(inspect.currentframe().f_code.co_name)

    try:
        response = requests.get(url, headers=headers)
        content = response.json()
    except (requests.exceptions.ConnectionError, socket.gaierror, urllib3.exceptions.MaxRetryError) as e:
        log.exception("failed to communicate with jokes api")
        raise RequestError(e)

    if not response.ok:
        raise RequestError(f"[{response.status_code}]{response.text}")

    return content


def action_random_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return escape_markdown(random.choice([
        "Hello World!",
        "This command is not supported",
    ]))


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

||{punchline}||
"""


def action_apininjas_facts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.api-ninjas.com/v1/facts?limit=1"
    api_ninjas_key = os.getenv("API_NINJAS_KEY")

    try:
        res = get_json_from_url(url, headers={"X-Api-Key": api_ninjas_key})
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        return escape_markdown(res[0]["fact"])


def action_apininjas_chuck_norris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.api-ninjas.com/v1/chucknorris"
    api_ninjas_key = os.getenv("API_NINJAS_KEY")

    try:
        res = get_json_from_url(url, headers={"X-Api-Key": api_ninjas_key})
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        return escape_markdown(res["joke"])


def action_apininjas_dad_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.api-ninjas.com/v1/dadjokes?limit=1"
    api_ninjas_key = os.getenv("API_NINJAS_KEY")

    try:
        res = get_json_from_url(url, headers={"X-Api-Key": api_ninjas_key})
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        return escape_markdown(res[0]["joke"])


def action_apininjas_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.api-ninjas.com/v1/quotes?limit=1"
    api_ninjas_key = os.getenv("API_NINJAS_KEY")

    try:
        res = get_json_from_url(url, headers={"X-Api-Key": api_ninjas_key})
    except RequestError as e:
        return escape_markdown("\n".join(e.args))
    if res:
        quote = escape_markdown(res[0]["quote"])
        author = escape_markdown(res[0]["author"])
        return fr""""{quote}"
\- _{author}_"""
