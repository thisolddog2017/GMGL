# -*- coding: utf-8 -*-
import os, logging, traceback, random
from uuid import uuid4

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import text_read, generate, text_process

help="""
[早報輸入格式](https://github.com/thisolddog2017/GMGL-pub/wiki/%E6%97%A9%E5%A0%B1%E8%BC%B8%E5%85%A5%E6%A0%BC%E5%BC%8F)
[Wiki](https://github.com/thisolddog2017/GMGL-pub/wiki)
[報告 Issue](https://github.com/thisolddog2017/GMGL-pub/issues)
"""

formatting_option_id = uuid4()
morning_news_option_id = uuid4()
morning_news_publish_prefix = "mnpub"

# State
morning_news_parsed = dict() # { uuid -> (post, items) }

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
    update.message.reply_markdown_v2(help)

def mk_notify_command(group_id):
    def notify(update, context):
        msg = update.message.text.split(' ', maxsplit=1)[-1].strip()
        update.message.bot.send_message(group_id, msg)
    return notify

def inlinequery(update, context):
    query = update.inline_query.query
    processed_query = query
    # try to parse the content on the go
    for f in [
        text_process.format_punctuations,
        text_process.format_numbers
    ]:
        processed_query = f(processed_query)


    results = [
        InlineQueryResultArticle(
            id=formatting_option_id,
            title="格式化",
            input_message_content=InputTextMessageContent(processed_query)),
    ]

    # morning news
    try:
        post, news_items = text_read.parse(processed_query)
        morning_news_formatted = '```\n{}\n```'.format(text_read.lay_out(post, news_items))
        morning_news_id = str(uuid4())
        morning_news_pub_callback_data = '{}.{}'.format(morning_news_publish_prefix, morning_news_id)
        morning_news_parsed[morning_news_id] = (post, news_items)
        results.append(
            InlineQueryResultArticle(
                id=morning_news_option_id,
                title="早報",
                input_message_content=InputTextMessageContent(
                    morning_news_formatted,
                    parse_mode=ParseMode.MARKDOWN_V2
                ),
                reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                    "發佈",
                    callback_data=morning_news_pub_callback_data
                ))
            ),
        )
    except text_read.InvalidContent as e:
        morning_news_error = "原文\n```\n{}\n```\n{}\n\\(關於輸入格式，見 /help\\)".format(query, e)
        results.append(
            InlineQueryResultArticle(
                id=morning_news_option_id,
                title="早報（輸入格式不符，點擊察看詳情）",
                input_message_content=InputTextMessageContent(
                    morning_news_error,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            )
        )

    update.inline_query.answer(results)

def mk_button(group_id, chat_instance_id):
    def button(update, context):
        query = update.callback_query
        if query.data.startswith(morning_news_publish_prefix):
            morning_news_id = query.data[len(morning_news_publish_prefix)+1:]
            # TODO not found in dict
            post, news_items = morning_news_parsed[morning_news_id]

            text = text_read.lay_out(post, news_items)
            # check room
            if query.chat_instance == chat_instance_id:
                out_path = generate.generate_image(post, news_items)

                query.bot.send_document(group_id, open(out_path, 'rb'))
                # update.message.reply_document(open(out_path, 'rb'), caption="...and Good Luck!")
                query.edit_message_text(
                    "*已發佈*\n\n```\n{}\n```".format(text),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                query.edit_message_text(
                    "*該房间無發佈權限*\n\n```\n{}\n```".format(text),
                    parse_mode=ParseMode.MARKDOWN_V2
                )


        query.answer()
    return button

def morning_news(update, context):
    update.message.reply_text("早報處理已升級爲聊天輸入框內操作，具體請見 /help")

def main():
    import sys
    token = sys.argv[1]
    group_id = sys.argv[2]
    chat_instance = sys.argv[3]

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(CallbackQueryHandler(mk_button(group_id, chat_instance)))

    # hidden switches
    dp.add_handler(CommandHandler("notify", mk_notify_command(group_id)))

    # on noncommand i.e morning news to process
    # TODO deprecate
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, morning_news))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
