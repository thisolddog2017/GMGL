# -*- coding: utf-8 -*-
import os, logging, traceback, random
from uuid import uuid4

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import gitlab
import gitlab.exceptions

import text_read, generate, text_process, layout

help="""
[早報輸入格式](https://github.com/thisolddog2017/GMGL-pub/wiki/%E6%97%A9%E5%A0%B1%E8%BC%B8%E5%85%A5%E6%A0%BC%E5%BC%8F)
[Wiki](https://github.com/thisolddog2017/GMGL-pub/wiki)
[報告 Issue](https://github.com/thisolddog2017/GMGL-pub/issues)
"""

morning_news_publish_prefix = "mnpub"

# bmdvY24K/ipmp
gitlab_project_id = 16409523

# State
morning_news_parsed = dict() # { uuid -> (post, items) }

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=os.environ.get('LOGLEVEL', 'INFO').upper())

logger = logging.getLogger(__name__)

def pub_to_gitlab(project, author_name, author_email, markdown_article):
    file_path = 'src/pages/article/'+markdown_article.name
    # check if file already exists
    try:
        # TODO use HEAD request to reduce data
        _old_file = project.files.get(file_path, ref='master')
        action = 'update'
    except gitlab.exceptions.GitlabGetError as e:
        if e.response_code == 404:
            # no such file
            action = 'create'
        else:
            raise e

    # See https://docs.gitlab.com/ce/api/commits.html#create-a-commit-with-multiple-files-and-actions
    # for actions detail
    data = {
        'branch': 'master',
        'commit_message': markdown_article.name,
        'author_name': author_name,
        'author_email': author_email,
        'actions': [
            {
                'action': action,
                'file_path': file_path,
                'content': markdown_article.content,
            }
        ]
    }
    commit = project.commits.create(data)

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
            id=uuid4(),
            title="格式化",
            input_message_content=InputTextMessageContent(processed_query)),
    ]

    # morning news
    try:
        post, news_items = text_read.parse(processed_query)
        morning_news_formatted = '```\n{}\n```'.format(layout.layout_text(post, news_items))
        morning_news_id = str(uuid4())
        morning_news_pub_callback_data = '{}.{}'.format(morning_news_publish_prefix, morning_news_id)
        morning_news_parsed[morning_news_id] = (post, news_items)
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
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
                id=uuid4(),
                title="早報（輸入格式不符，點擊察看詳情）",
                input_message_content=InputTextMessageContent(
                    morning_news_error,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            )
        )

    update.inline_query.answer(results)

def handle_morning_news_publish(query, author_name, author_email, allowed_chat_instance, group_id, morning_news_id, gitlab_project):
    text = None
    try:
        morning_news_found = morning_news_parsed.get(morning_news_id)
        if morning_news_found is None:
            raise Exception("找不到該早報信息，請重新發送早報")
        post, news_items = morning_news_found

        text = layout.layout_text(post, news_items)
        # check room
        if query.chat_instance == allowed_chat_instance:
            # generate image
            out_path = generate.generate_image(post, news_items)

            query.bot.send_document(group_id, open(out_path, 'rb'))
            # publish to ngocn2
            markdown_article = layout.layout_markdown_article(post, news_items, author_name)
            pub_to_gitlab(gitlab_project, author_name, author_email, markdown_article)

            query.edit_message_text(
"""*已發佈*

\\- 圖片發送至組
\\- 網頁（需約 15 分鐘上線）: [ngocn2](https://ngocn2.org/article/{}/)

```
{}
```
""".format(markdown_article.name[:-3], text),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            raise Exception("該房间無發佈權限")
    except Exception as e:
        logger.exception("Error when publishing: %r", text)
        query.edit_message_text(
"""*發佈失敗*
詳情
```
{}
```

原文
```
{}
```
""".format(e, text or "<無法獲取>"),
            parse_mode=ParseMode.MARKDOWN_V2
        )

def mk_button(group_id, chat_instance_id, gitlab_project):
    def button(update, context):
        query = update.callback_query
        if query.data.startswith(morning_news_publish_prefix):
            author_name = query.from_user.first_name
            author_email = 'it.ngocn@gmail.com'
            morning_news_id = query.data[len(morning_news_publish_prefix)+1:]
            handle_morning_news_publish(query, author_name, author_email, chat_instance_id, group_id, morning_news_id, gitlab_project)


        query.answer()
    return button

def morning_news(update, context):
    update.message.reply_text("早報處理已升級爲聊天輸入框內操作，具體請見 /help")

def main():
    import sys
    token = sys.argv[1]
    group_id = sys.argv[2]
    chat_instance = sys.argv[3]
    gitlab_token = sys.argv[4]

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    gl = gitlab.Gitlab('https://gitlab.com', private_token=gitlab_token)

    gitlab_project = gl.projects.get(gitlab_project_id, lazy=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(CallbackQueryHandler(mk_button(group_id, chat_instance, gitlab_project)))

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
