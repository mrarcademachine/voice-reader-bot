import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
)

import extractor
from config import API_TOKEN

MESSAGE_CHAR_LIMIT = 4096

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
    )


async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):
    answer_message = ("Привет! Если тебе лень слушать чью-то голосовуху — "
                      "перешли её мне, и я переведу её в текст.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer_message
        )


async def transcribe_voice(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
    autoanswer_message = "Слушаю и записываю..."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=autoanswer_message
        )

    voice_message_audio = await download_audio(update, context)
    voice_text = extractor.get_text(voice_message_audio)

    # If character count exceeds 4096, splits the message into multiple
    # and sends them consecutively.
    for answer_message in range(0, len(voice_text), MESSAGE_CHAR_LIMIT):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=voice_text[answer_message:answer_message+MESSAGE_CHAR_LIMIT]
        )


async def download_audio(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> Path:
    voice_file = await context.bot.get_file(update.message.voice)
    voice_file_path = Path('voice_message.ogg')
    await voice_file.download_to_drive(voice_file_path)
    return voice_file_path


async def unknown_input(update: Update,
                        context: ContextTypes.DEFAULT_TYPE):
    answer_message = ("Пришли мне голосовое сообщение,"
                      "и я переведу его в текст.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer_message
        )


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(filters.VOICE, transcribe_voice)
    unknown_handler = MessageHandler(~filters.VOICE, unknown_input)

    application.add_handlers(
        [
            start_handler,
            voice_handler,
            unknown_handler
        ]
    )
    application.run_polling()
