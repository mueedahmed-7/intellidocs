import unittest

from member3.voice.tts.text_to_speech import _plain_speech_text, _select_voice


class Voice:
    def __init__(self, name, voice_id):
        self.name = name
        self.id = voice_id


class TextToSpeechTests(unittest.TestCase):
    def test_prefers_a_natural_voice_hint_when_available(self):
        voices = [Voice("Microsoft Zira", "zira"), Voice("Microsoft Aria Online", "aria")]
        self.assertEqual(_select_voice(voices, ("aria", "zira")).name, "Microsoft Aria Online")

    def test_markdown_is_cleaned_before_speech(self):
        text = "# Summary\n- Read [the guide](https://example.test) and `run it`."
        self.assertEqual(_plain_speech_text(text), "Summary Read the guide and run it.")
