import inspect

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

    action = actions.actions.random()

    log.debug(f"chose {action.__name__}")
    message = action(update, context)
    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
