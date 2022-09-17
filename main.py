#!/usr/bin/env python

"""
Please set the 'telegram_token' as an environment variable
"""

import logging
import os

from idp_renew.auth import *
from idp_renew.register import Register

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logger = logging.getLogger(__name__)


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explains how to use the bot."""

    if len(context.args) != 2:
        await update.message.reply_text("Gebruik /login <email> <wachtwoord> om in te loggen")
    else:
        # Get the username and password from the message
        username, password = update.message.text.split(" ")[1:]

        # Save the username and password in the user_data
        context.user_data[update.effective_chat.id] = [username, password]

        await update.message.reply_text("Je bent ingelogd!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with the date buttons."""

    # Check if the user is logged in
    if update.effective_chat.id not in context.user_data:
        await update.message.reply_text("Je bent niet ingelogd! gebruik /login <email> <wachtwoord> om in te loggen.")
        return
    else:
        keyboard = [
            [
                InlineKeyboardButton("Vrijdag", callback_data="vrijdag"),
                InlineKeyboardButton("Zaterdag", callback_data="zaterdag"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Meld je aan", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """This code runs when one of the buttons are clicked."""

    query = update.callback_query
    user = AuthUser(context.user_data[update.effective_chat.id][0], context.user_data[update.effective_chat.id][1])
    # user = AuthUser(os.getenv("djo_user"), os.getenv("djo_pass"))

    server = AuthServer(user)
    register = Register(server)

    try:
        server.authenticate()
    except Exception as e:
        await query.edit_message_text("Je gebruikersnaam of wachtwoord is niet correct! pas het aan met /login")
        # await query.message.reply_markdown(f" Debug:\n`{str(e)}`")
        return

    pods = register.pods()

    for pod in pods:
        if not pod.available or pod.closed:
            print("Niet beschikbaar of gesloten")
            continue

        if pod.available == 0:
            print("Niet beschikbaar")
            continue

        if query.data == "vrijdag":
            if pod.pod == "e":
                # try to register
                try:
                    pod.register()
                    print("Aangemeld voor Vrijdag")
                except:
                    print("Error bij aanmelden voor Vrijdag")
        else:
            if pod.pod == "m":
                # try to register
                try:
                    pod.register()
                    print("Aangemeld voor Zaterdag")
                except:
                    print("Error bij aanmelden voor Zaterdag")

    await query.answer()
    await query.edit_message_text(text=f"Je bent aangemeld voor {query.data.capitalize()}.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""

    await update.message.reply_markdown_v2("""
    *__DJO Aanmelden__*
*Gebruik /login \<email\> \<wachtwoord\> om in te loggen*
*Gebruik /start om je aan te melden*
    """)


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder().token(os.getenv("telegram_token")).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("login", login))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
