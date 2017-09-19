"""
Support for the eSpeak NG speech service.

2017 by G.Bartsch
"""
import os
import sys
import tempfile
import shutil
import subprocess
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.tts import Provider, PLATFORM_SCHEMA, CONF_LANG

from espeakng import ESpeakNG

_LOGGER = logging.getLogger(__name__)

SUPPORT_LANGUAGES = ['afrikaans', 'amharic', 'aragonese', 'arabic', 'assamese', 'azerbaijani',
                     'bulgarian', 'bengali', 'bosnian', 'catalan', 'czech', 'welsh', 'danish',
                     'german', 'greek', 'en-westindies', 'english', 'en-scottish', 'english-north',
                     'english_wmids', 'english_rp', 'english-us', 'esperanto', 'spanish', 'spanish-latin-am',
                     'estonian', 'basque', 'Persian+English-UK', 'Persian+English-US', 'persian-pinglish',
                     'finnish', 'french-Belgium', 'french', 'irish-gaeilge', 'scottish-gaelic',
                     'guarani', 'greek-ancient', 'gujarati', 'hindi', 'croatian', 'hungarian', 'armenian',
                     'armenian-west', 'interlingua', 'indonesian', 'icelandic', 'italian', 'lojban',
                     'japanese', 'georgian', 'greenlandic', 'kannada', 'Korean', 'kurdish', 'kyrgyz',
                     'latin', 'lingua_franca_nova', 'lithuanian', 'latvian', 'macedonian', 'malayalam',
                     'marathi', 'malay', 'maltese', 'burmese', 'nahuatl-classical', 'nepali', 'dutch',
                     'norwegian', 'oromo', 'oriya', 'punjabi', 'papiamento', 'polish', 'brazil', 'portugal',
                     'romanian', 'russian', 'sinhala', 'slovak', 'slovenian', 'albanian', 'serbian', 'swedish',
                     'swahili', 'tamil', 'telugu', 'setswana', 'turkish', 'tatar', 'urdu', 'vietnam',
                     'vietnam_hue', 'vietnam_sgn', 'Mandarin', 'cantonese']

DEFAULT_LANG  = 'english-us'
DEFAULT_PITCH = 50
DEFAULT_SPEED = 175

CONF_PITCH = 'pitch'
CONF_SPEED = 'speed'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_LANG,  default=DEFAULT_LANG):  vol.In(SUPPORT_LANGUAGES),
    vol.Optional(CONF_PITCH, default=DEFAULT_PITCH): cv.positive_int,
    vol.Optional(CONF_SPEED, default=DEFAULT_SPEED): cv.positive_int,
})


def get_engine(hass, config):
    """Set up eSpeak NG speech component."""
    if shutil.which("espeak-ng") is None:
        _LOGGER.error("'espeak-ng' was not found")
        return False
    return ESpeakNGProvider(config)


class ESpeakNGProvider(Provider):
    """The eSpeak NG TTS API provider."""

    def __init__(self, conf):
        """Initialize eSpeak NG TTS provider."""
        self._lang  = conf[CONF_LANG]
        self._speed = conf[CONF_SPEED]
        self._pitch = conf[CONF_PITCH]
        self.name = 'eSpeakNGTTS'
        _LOGGER.debug("espeak-ng: init done, language is %s" % self._lang)

    @property
    def default_language(self):
        """Return the default language."""
        return self._lang

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    def get_tts_audio(self, message, language, options=None):
        """Load TTS using eSpeakNG."""

        _LOGGER.debug('espeakng message is %s, language is %s' % (repr(message), repr(language)))

        esng = ESpeakNG(voice=language, speed=self._speed, pitch=self._pitch)

        data = esng.synth_wav(message)

        return ("wav", data)

