import inspect

import telegram.constants
from telegram import Update
from telegram.ext import ContextTypes

from . import actions
from .actions import MessageType
from .logger import create_logger


def send_telegram_error_message(message: str, *, _: Update = None):
    log = create_logger(inspect.currentframe().f_code.co_name)

    log.error(message)


async def random_action(update: Update, _: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)

    text = (
        update.effective_message.text if update.effective_message.text else update.effective_message.caption
    )
    if not (text and text.startswith("/")):
        return

    command = update.effective_message.text.replace("/", "")
    command = command.split("@", maxsplit=1)[0]
    action = actions.actions.find(command)
    if not action:
        action = actions.actions.random()

    log.debug(f"chose {action.name()}")
    message = action()
    return await message.send(update)


async def weights(update: Update, _: ContextTypes.DEFAULT_TYPE):
    message = str(actions.actions)
    return await update.effective_message.reply_text(
        message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
    )
