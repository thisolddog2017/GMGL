# -*- coding: utf-8 -*-
import os, logging, traceback, random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import regex_read, generate, formats

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=os.environ.get('LOGLEVEL', 'INFO').upper())

logger = logging.getLogger(__name__)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Yes, I'm listening.")

def help_command(update, context):
    """Send a message when the command /help is issued."""
    # TODO support more commands
    update.message.reply_text(regex_read.__doc__)

def mk_notify_command(group_id):
    def notify(update, context):
        msg = ' '.join(context.args)
        update.message.bot.send_message(group_id, msg)
    return notify

def bless_image(update, context):
    """Echo the user message."""
    try:
        input = update.message.text
        # do a global formatting first
        corrected = []
        for f, name in [ (formats.format_punctuations, "punctuations"),
                         (formats.format_numbers, "numbers / English") ]:
            input1 = f(input)
            if input1 != input:
                input = input1
                corrected.append(name)

        post, news_items = regex_read.parse(input)
        formatted = regex_read.lay_out(post, news_items)

        update.message.reply_text("Good Morning...")
        if corrected:
            update.message.reply_text(
                "I see you are not being careful with {} - so I've corrected it for you:".format(
                    ' and '.join(
                        x for x in [', '.join(corrected[:-1]), corrected[-1]] if x
                    )
                )
            )
        else:
            update.message.reply_text("Bravo! You've made no mistakes that I can spot. In any case, here's the well formatted piece:")
        update.message.reply_text(formatted)

        out_path = generate.generate_image(post, news_items)
        update.message.reply_document(open(out_path, 'rb'), caption="...and Good Luck!")
    except regex_read.InvalidContent:
        logger.info("[%r] Failed to parse content: %r", update.message.chat.first_name, update.message.text)
        reply = random.choice([
            "You're not being serious with me, are you?",
            "Big Brother says when I grow up one day... I might understand what you mean.",
            "No time to waste here, my dear."
        ])
        update.message.reply_text(
            "{}\n\n(Your text format looks wrong, try /help)".format(reply)
        )
    except Exception as e:
        logger.exception("Error when handling message: %r", update.message.text)
        update.message.reply_text("Sh*t happened... Please ask for Big Brother. Here's what I was chewing on:\n\n{}".format(traceback.format_exc()))

def main():
    import sys
    token = sys.argv[1]
    group_id = sys.argv[2]

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # hidden switches
    dp.add_handler(CommandHandler("notify", mk_notify_command(group_id)))

    # on noncommand i.e morning news to process
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, bless_image))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
