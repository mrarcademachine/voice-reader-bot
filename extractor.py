import json
from pathlib import Path

import speech_recognition
from pydub import AudioSegment


def get_text(audio_handle: Path) -> str:
    converted_audio_handle = _convert_from_ogg_to_wav(audio_handle)
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.AudioFile(str(converted_audio_handle)) as source:
        audio = recognizer.record(source)

    try:
        raw_data = recognizer.recognize_vosk(audio)
        text = json.loads(raw_data)["text"]
    except Exception:
        text = "Ошибка расшифровки"

    _remove_temporary_files([audio_handle, converted_audio_handle])
    return text


def _convert_from_ogg_to_wav(audio_handle: Path) -> Path:
    ogg_audio = AudioSegment.from_ogg(audio_handle)
    wav_file_path = Path("voice_message.wav")
    ogg_audio.export(out_f=wav_file_path, format='wav')
    return wav_file_path


def _remove_temporary_files(files: list) -> None:
    for file in files:
        file.unlink(missing_ok=True)
