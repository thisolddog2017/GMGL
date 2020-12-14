# -*- coding: utf-8 -*-
import os, logging
from uuid import uuid4

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import gitlab
import gitlab.exceptions

import text_read, generate, text_process, layout

help="""
*早報*

```
/zaobao 早報輸入…
```
- [早報輸入格式](https://github.com/thisolddog2017/GMGL-pub/wiki/%E6%97%A9%E5%A0%B1%E8%BC%B8%E5%85%A5%E6%A0%BC%E5%BC%8F)
- [Wiki](https://github.com/thisolddog2017/GMGL-pub/wiki)
- [報告 Issue](https://github.com/thisolddog2017/GMGL-pub/issues)
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

def full_text_process(query):
    processed_query = query
    for f in [
        text_process.format_punctuations,
        text_process.format_numbers
    ]:
        processed_query = f(processed_query)
    return processed_query

def mk_telegram_msg_link(chat_id, msg_id):
    # https://stackoverflow.com/questions/51065460/link-message-by-message-id-via-telegram-bot
    chat_id = str(chat_id)
    if chat_id.startswith('-'):
        chat_id = chat_id[4:]
    return 'https://t.me/c/{}/{}'.format(chat_id, msg_id)

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
    return 'https://ngocn2.org/article/{}/'.format(markdown_article.name[:-3])

def get_command_payload(text):
    return text.split(' ', maxsplit=1)[-1].strip()

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("我是…… 算了，直接看 /help 吧")

def help_command(update, context):
    """Send a message when the command /help is issued."""
    # TODO support more commands
    update.message.reply_markdown(help)

def mk_notify_command(group_id):
    def notify(update, context):
        msg = get_command_payload(update.message.text)
        update.message.bot.send_message(group_id, msg)
    return notify

def format_command(update, context):
    processed_query = full_text_process(get_command_payload(update.message.text))
    update.message.reply_text(processed_query)

def mk_morning_news_command(group_id):
    def morning_news_command(update, context):
        processed_query = full_text_process(get_command_payload(update.message.text))
        processed_query_markdown = full_text_process(get_command_payload(update.message.text_markdown_urled))

        # morning news
        try:
            post, news_items = text_read.parse(processed_query, content_markdown=processed_query_markdown)
            morning_news_formatted = layout.layout_markdown_message(post, news_items)

            kwargs={}
            if update.message.chat.id == group_id:
                # add publish option
                morning_news_id = str(uuid4())
                morning_news_pub_callback_data = '{}.{}'.format(morning_news_publish_prefix, morning_news_id)
                morning_news_parsed[morning_news_id] = (post, news_items)
                kwargs['reply_markup'] = InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                    "發佈",
                    callback_data=morning_news_pub_callback_data
                ))
            update.message.reply_markdown(
                morning_news_formatted,
                disable_web_page_preview=True,
                **kwargs
            )

        except text_read.InvalidContent as e:
            morning_news_error = """{}
(關於輸入格式，見 /help)
""".format(e)
            update.message.reply_markdown(
                morning_news_error
            )
    return morning_news_command

def handle_morning_news_publish(query, author_name, author_email, group_id, morning_news_id, gitlab_project):
    text = None
    try:
        morning_news_found = morning_news_parsed.get(morning_news_id)
        if morning_news_found is None:
            raise Exception("找不到該早報信息，請重新發送早報")
        post, news_items = morning_news_found

        text = layout.layout_markdown_message(post, news_items)
        # check room
        if query.message.chat.id == group_id:
            # generate image
            out_path = generate.generate_image(post, news_items)

            # publish to ngocn2
            markdown_article = layout.layout_markdown_article(post, news_items, author_name)
            pub_url = pub_to_gitlab(gitlab_project, author_name, author_email, markdown_article)
            published_message = query.message.reply_document(
                open(out_path, 'rb'),
                caption="""*發佈信息*

- 圖片見上
- {} 15-20 分鐘後上線
""".format(pub_url),
                parse_mode=ParseMode.MARKDOWN
            )

            # remove the publish button
            # add the webpage link
            # turn on preview
            query.edit_message_text(
                '{}\n\n{}'.format(pub_url, query.message.text_markdown),
                reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                    "已發佈，點擊察看信息",
                    url=mk_telegram_msg_link(group_id, published_message.message_id)
                )),
                disable_web_page_preview=False,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            raise Exception("該房间無發佈權限")
    except Exception as e:
        logger.exception("Error when publishing: %r", text)
        query.message.reply_markdown(
"""*發佈失敗*
詳情
```
{}
```
""".format(e)
        )

def mk_button(group_id, gitlab_project):
    def button(update, context):
        query = update.callback_query
        if query.data.startswith(morning_news_publish_prefix):
            author_name = query.from_user.first_name
            author_email = 'it.ngocn@gmail.com'
            morning_news_id = query.data[len(morning_news_publish_prefix)+1:]
            handle_morning_news_publish(query, author_name, author_email, group_id, morning_news_id, gitlab_project)
        query.answer()

    return button

def main():
    import sys
    token = sys.argv[1]
    group_id = int(sys.argv[2])
    gitlab_token = sys.argv[3]

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
    dp.add_handler(CommandHandler("geshi", format_command))
    dp.add_handler(CommandHandler("zaobao", mk_morning_news_command(group_id)))
    dp.add_handler(CallbackQueryHandler(mk_button(group_id, gitlab_project)))

    # hidden switches
    dp.add_handler(CommandHandler("notify", mk_notify_command(group_id)))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
