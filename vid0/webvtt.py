from math import floor


def whisper_json_to_webvtt(input_whisper_json):
    ret = []
    ret.append("WEBVTT")
    ret.append("")

    for c in input_whisper_json["transcription"]["segments"]:
        ret.append(webvtt_timestamp(c["start"]) + " --> " + webvtt_timestamp(c["end"]))
        assert "-->" not in c["text"]
        ret.append(c["text"].strip())
        ret.append("")

    return "\n".join(ret)


def webvtt_timestamp(seconds):
    rounded_seconds = round(seconds * 1000) / 1000
    minutes = floor(rounded_seconds / 60)
    rounded_seconds -= minutes * 60

    hours = minutes // 60
    minutes = minutes % 60

    seconds_only = floor(rounded_seconds)
    fraction = round(1000 * (rounded_seconds - seconds_only))

    hours_string = ""
    if hours > 0:
        hours_string = str(hours) + ":"

    return f"{hours_string}{minutes:02d}:{seconds_only:02d}.{fraction:03d}"
