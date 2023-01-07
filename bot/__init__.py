import inspect
import random

import telegram.constants
from telegram import Update
from telegram.ext import ContextTypes

from . import actions
from .logger import create_logger


def send_telegram_error_message(message: str, *, update: Update = None):
    log = create_logger(inspect.currentframe().f_code.co_name)

    log.error(message)


async def random_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)

    if not (update.effective_message.text and update.effective_message.text.startswith("/")):
        return lambda x: x

    possible_actions = [action for action in dir(actions) if action.startswith("action_")]
    if not possible_actions:
        return send_telegram_error_message("no actions available", update=update)

    log.debug(f"choose random action from {len(possible_actions)} actions")
    action_name = random.choice(possible_actions)

    log.debug(f"chose {action_name}")
    action = getattr(actions, action_name)
    message = action(update, context)
    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
