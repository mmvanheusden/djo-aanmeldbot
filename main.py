#!/usr/bin/env python

# pylint: disable=unused-argument, wrong-import-position

# This program is dedicated to the public domain under the CC0 license.


"""

Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out

 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.

"""

import logging
import os
from datetime import date

from idp_renew.auth import *
from idp_renew.register import Register

from telegram import __version__ as TG_VER

try:

    from telegram import __version_info__

except ImportError:

    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(

        f"This example is not compatible with your current PTB version {TG_VER}. To view the "

        f"{TG_VER} version of this example, "

        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"

    )

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""

    keyboard = [
        [InlineKeyboardButton("Aanmelden", callback_data="3")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Meld je aan", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed

    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    print("klik")

    user = AuthUser(os.getenv("djo_user"), os.getenv("djo_pass"))

    server = AuthServer(user)
    register = Register(server)

    server.authenticate()
    pods = register.pods()

    for pod in pods:
        # exceptions to registering
        # print(pod.name)
        # print(dir(pod))
        print(pod.pod)

        if not pod.available or pod.closed:
            print("niet beschikbaar of gesloteb")
            continue

        if pod.available == 0:
            print("niet beschikbaar")
            continue

        if pod.pod == "e":
            # try to register
            try:
                pod.register()
                print("aangemeld")
            except:
                print("aanmeld error")

    await query.answer()

    await query.edit_message_text(text=f"Je bent aangemeld.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""

    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder().token(os.getenv("telegram_token")).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C

    application.run_polling()


if __name__ == "__main__":
    main()
