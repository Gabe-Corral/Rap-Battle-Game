from gtts import gTTS
import os
import pyttsx3
import vlc

class TextToSpeech:

    def __init__(self, text):
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', 110)
        engine.say(text)
        engine.runAndWait()
