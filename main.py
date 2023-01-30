import inspect
import os
import sys

import telegram.ext
from telegram.ext import ApplicationBuilder

import bot
from bot.logger import create_logger


def get_bot_token_or_die(env_variable: str = "BOT_TOKEN"):
    logger = create_logger(inspect.currentframe().f_code.co_name)
    if token := os.getenv(env_variable):
        return token

    logger.error(f"failed to retrieve token from environment (`{env_variable}`)")
    sys.exit(1)


def main():
    bot_token = get_bot_token_or_die()
    application = ApplicationBuilder().token(bot_token).build()

    random_handler = telegram.ext.MessageHandler(telegram.ext.filters.ALL, bot.random_action)
    application.add_handler(random_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
