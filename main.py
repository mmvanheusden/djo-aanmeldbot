#!/usr/bin/env python

"""
Please set the 'telegram_token' as an environment variable
"""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, PicklePersistence

from idp_renew.auth import *
from idp_renew.register import Register

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log in to the bot using DJO credentials."""

    # Check if the user is already logged in
    if update.effective_chat.id not in context.user_data:
        if len(context.args) != 2:
            await update.message.reply_text("Gebruik /login <email> <wachtwoord> om in te loggen")
        else:
            # Get the username and password from the message
            username, password = update.message.text.split(" ")[1:]

            # Save the username and password in the user_data
            context.user_data[update.effective_chat.id] = [username, password]

            await update.message.reply_text("Je bent ingelogd! /aanmelden om je aan te melden")
    else:
        await update.message.reply_text("Je bent al ingelogd! log uit met /logout")


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs the user out."""

    # Check if the user is logged in
    if update.effective_chat.id not in context.user_data:
        await update.message.reply_text("Je bent niet ingelogd! gebruik /login <email> <wachtwoord> om in te loggen.")
        return
    else:
        del context.user_data[update.effective_chat.id]
        await update.message.reply_text("Je bent uitgelogd!")


async def aanmelden(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with the aanmeld buttons."""

    # Check if the user is logged in
    if update.effective_chat.id not in context.user_data:
        await update.message.reply_text("Je bent niet ingelogd! gebruik /login <email> <wachtwoord> om in te loggen.")
        return
    else:
        keyboard = [
            [
                InlineKeyboardButton("Vrijdag", callback_data="vrijdagaanmelden"),
                InlineKeyboardButton("Zaterdag", callback_data="zaterdagaanmelden"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Meld je aan", reply_markup=reply_markup)


async def afmelden(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with the afmeld buttons."""

    # Check if the user is logged in
    if update.effective_chat.id not in context.user_data:
        await update.message.reply_text("Je bent niet ingelogd! gebruik /login <email> <wachtwoord> om in te loggen.")
        return
    else:
        keyboard = [
            [
                InlineKeyboardButton("Vrijdag", callback_data="vrijdagafmelden"),
                InlineKeyboardButton("Zaterdag", callback_data="zaterdagafmelden"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Meld je af", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """This code runs when one of the buttons are clicked."""

    query = update.callback_query
    user = AuthUser(context.user_data[update.effective_chat.id][0], context.user_data[update.effective_chat.id][1])

    server = AuthServer(user)
    register = Register(server)

    try:
        server.authenticate()
    except Exception as e:
        await query.edit_message_text(
            "Je gebruikersnaam of wachtwoord is niet correct! pas het aan met /login <email> <wachtwoord>")
        return

    pods = register.pods()

    for pod in pods:
        if not pod.available or pod.closed:
            if pod.pod == "e" and query.data == "vrijdagaanmelden":
                await query.edit_message_text(f"Het is niet mogelijk om je aan te melden voor Vrijdag")
                return
            elif pod.pod == "f" and query.data == "zaterdagaanmelden":
                await query.edit_message_text(f"Het is niet mogelijk om je aan te melden voor Zaterdag")
                return
            print("Niet beschikbaar")
            continue

        if "vrijdag" in query.data:
            if pod.pod == "e":
                try:
                    if "aanmelden" in query.data:
                        pod.register()
                        print("Aangemeld voor Vrijdag")
                        await query.edit_message_text("Je bent aangemeld voor Vrijdag! /afmelden om je af te melden")
                    else:
                        pod.deregister()
                        print("Afgemeld voor Vrijdag")
                        await query.edit_message_text("Je bent afgemeld voor Vrijdag! /aanmelden om je aan te melden")
                except:
                    print("Error bij aanmelden/afmelden voor Vrijdag")
        else:
            if pod.pod == "m":
                try:
                    if "aanmelden" in query.data:
                        pod.register()
                        print("Aangemeld voor Zaterdag")
                        await query.edit_message_text("Je bent aangemeld voor Zaterdag! /afmelden om je af te melden")
                    else:
                        pod.deregister()
                        print("Afgemeld voor Zaterdag")
                        await query.edit_message_text("Je bent afgemeld voor Zaterdag! /aanmelden om je aan te melden")
                except:
                    print("Error bij aanmelden/afmelden voor Zaterdag")

    await query.answer()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""

    await update.message.reply_markdown_v2("""
    *__DJO Aanmelden__*
*Gebruik /aanmelden om aan te melden*
*Gebruik /afmelden om af te melden*
*Gebruik /login \<email\> \<wachtwoord\> om in te loggen*
*Gebruik /logout om uit te loggen*
    """)


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    persistence = PicklePersistence(filepath="aanmeldbot")
    application = Application.builder().token(os.getenv("telegram_token")).persistence(persistence).build()

    application.add_handler(CommandHandler(("start", "help"), start))
    application.add_handler(CommandHandler("aanmelden", aanmelden))
    application.add_handler(CommandHandler("afmelden", afmelden))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("logout", logout))

    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
