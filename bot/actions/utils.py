import inspect
import socket
from typing import Dict, Optional

import requests as requests
import urllib3 as urllib3

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


def _split_messages(lines):
    message_length = 4096
    messages = []
    current_length = 0
    current_message = 0
    for line in lines:
        if len(messages) <= current_message:
            messages.append([])

        line_length = len(line)
        if current_length + line_length + len(messages[current_message]) < message_length:
            current_length += line_length
            messages[current_message].append(line)
        else:
            current_length = 0
            current_message += 1

    return messages
