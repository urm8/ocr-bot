import logging
import os
from datetime import datetime
from functools import partial
from io import BytesIO

from telegram import Bot, ChatAction, Document, Message, PhotoSize, Update
from telegram.ext import CallbackContext, MessageHandler, Updater

import service

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

log = logging.getLogger('bot-main')

def get_token() -> str:
    try:
        token = open('secret.txt').read().strip()
    except FileNotFoundError: 
        token = os.environ['token']
    logging.info('start with token: %s', token)
    return token


def configure(bot: Bot) -> Updater:
    updater = Updater(bot=bot, use_context=True, request_kwargs={
        'read_timeout': 15,
        'connect_timeout': 15
    })
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(None, callback=photo_to_text, pass_chat_data=True, pass_user_data=True))
    updater.start_polling(poll_interval=0.5, timeout=30, read_latency=15)
    return updater

def photo_to_text(update: Update, ctx: CallbackContext):
    log.info('got msg:\n\t%s\nfrom update:\n\t%s', update.message, update)
    msg: Message = update.message

    bot = msg.bot

    log.debug('send typing animation')
    bot.send_chat_action(msg.chat_id, action=ChatAction.TYPING)

    if not (msg.photo or msg.document):
        log.warning('fatal, no photo ')
        msg.reply_text('no photo')
        return
    try:
        mime_type = None
        if msg.photo:
            *_, biggest_photo = msg.photo
            photo: PhotoSize = biggest_photo.get_file()
            
        else:
            photo = msg.document.get_file()
            mime_type = msg.document.mime_type
        logging.info('got file: %s', photo)
        bits = photo.download_as_bytearray()
        doc_str, ext = service.convert(bits, mime_type=mime_type)
        fn = datetime.now().strftime(f'%d_%m_%H_%M.{ext}')
        bot.send_document(msg.chat_id, BytesIO(doc_str), filename=fn)
    except Exception:
        log.warning('something nasty happened', exc_info=True)


if __name__ == '__main__':
    bot = Bot(token=get_token())
    configure(bot).idle()
