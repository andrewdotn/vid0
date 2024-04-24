import pytest

from vid0.webvtt import whisper_json_to_webvtt, webvtt_timestamp

SAMPLE_INPUT = {
    "transcription": {
        "segments": [
            {"start": 0, "end": 15.3, "text": "Hello, world"},
            {"start": 18.4, "end": 22.5, "text": "This is a test"},
            {"start": 3601.0, "end": 3603.2, "text": "Well that was more than an hour"},
        ]
    }
}

EXPECTED_OUTPUT = """\
WEBVTT

00:00.000 --> 00:15.300
Hello, world

00:18.400 --> 00:22.500
This is a test

1:00:01.000 --> 1:00:03.200
Well that was more than an hour
"""


def test_whisper_json_to_webvtt():
    assert whisper_json_to_webvtt(SAMPLE_INPUT) == EXPECTED_OUTPUT


@pytest.mark.parametrize(
    ("input_time", "expected"),
    [
        [0.0, "00:00.000"],
        [60.0, "01:00.000"],
        [60.15, "01:00.150"],
        [63.1, "01:03.100"],
        [60 - 1 / 29.97, "00:59.967"],
        [59.999, "00:59.999"],
        [59.9995, "01:00.000"],
        [59.994, "00:59.994"],
        [601.0, "10:01.000"],
        [3601.0, "1:00:01.000"],
    ],
)
def test_webtt_timestamp(input_time, expected):
    assert webvtt_timestamp(input_time) == expected
