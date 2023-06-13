import json
import logging
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
)

from config import TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Если тебе лень слушать чью-то голосовуху — перешли её мне, и я переведу её в текст."
    )


async def voice_transcribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text='Слушаю и записываю...'
    )
    voice_file = await context.bot.get_file(update.message.voice)
    voice_path = Path('voice_message.ogg')
    await voice_file.download_to_drive(str(voice_path))

    orig_file = AudioSegment.from_ogg(str(voice_path))
    wav_path = Path("voice_message.wav")
    orig_file.export(out_f=str(wav_path), format='wav')

    r = sr.Recognizer()
    with sr.AudioFile('voice_message.wav') as source:
        audio = r.record(source)

    try:
        result = r.recognize_vosk(audio)
        json_data = json.loads(result)
        text = json_data["text"]
    except Exception:
        text = "Ошибка расшифровки"

    for x in range(0, len(text), 4096):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text[x:x+4096]
        )

    voice_path.unlink(missing_ok=True)
    wav_path.unlink(missing_ok=True)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Пришли мне голосовое сообщение, и я переведу её в текст.'
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(filters.VOICE, voice_transcribe)
    unknown_handler = MessageHandler(~filters.VOICE, unknown)

    application.add_handlers([start_handler, voice_handler, unknown_handler])
    application.run_polling()
