import speech_recognition as sr
import pyaudio
import pygame
import os
import tempfile
from gtts import gTTS
from io import BytesIO


def listen(lang='zh-tw'):
    rg = sr.Recognizer()
    with sr.Microphone() as source:
        audioData = rg.listen(source)
        try:
            text = rg.recognize_google(audioData, language=lang, show_all=True)
        except:
            text = ''
    return text


def speak(text, lang='zh-tw'):
    # 建立播放用的語音檔
    active_mp3 = 'tmp.mp3'
    pygame.mixer.init()

    tts = gTTS(text, lang=lang)
    tts.save(active_mp3)
    pygame.mixer.music.load(active_mp3)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.music.unload()

    # 刪除語音檔
    try:
        os.unlink(active_mp3)
    except:
        pass


if __name__ == "__main__":
    texts = listen()
    speak(texts['alternative'][0]['transcript'])
    print(texts)
