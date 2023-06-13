import os
import json
import logging
import speech_recognition as sr
from config import TOKEN
from pydub import AudioSegment
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

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
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Слушаю и записываю...')
    voice_file = await context.bot.get_file(update.message.voice)
    await voice_file.download_to_drive('voice_message.ogg')
    orig_file = AudioSegment.from_ogg('voice_message.ogg')
    orig_file.export(out_f='voice_message.wav', format='wav')
    r = sr.Recognizer()
    with sr.AudioFile('voice_message.wav') as source:
        audio = r.record(source)
    try:
        result = r.recognize_vosk(audio)
        json_data = json.loads(result)
        text = json_data["text"]
    except sr.UnknownValueError:
        text = "Ошибка расшифровки"
    except sr.RequestError:
        text = "Не могу подключиться к сервису расшифровки"
    for x in range(0, len(text), 4096):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text[x:x+4096])
    os.system('rm voice_message.ogg voice_message.wav')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Пришли мне голосовое сообщение, и я переведу её в текст.')


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(filters.VOICE, voice_transcribe)
    unknown_handler = MessageHandler(~filters.VOICE, unknown)

    application.add_handlers([start_handler, voice_handler, unknown_handler])
    application.run_polling()
