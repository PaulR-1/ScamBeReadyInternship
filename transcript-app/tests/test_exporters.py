from app.services import exporters

SEGMENTS = [
    {"start": 0.0, "end": 2.5, "text": "Kumusta, are you okay?"},
    {"start": 2.5, "end": 4.0, "text": "Oo naman, I'm fine."},
]


def test_srt_timestamp_formatting():
    assert exporters.srt_timestamp(0) == "00:00:00,000"
    assert exporters.srt_timestamp(3661.5) == "01:01:01,500"
    assert exporters.vtt_timestamp(3661.5) == "01:01:01.500"
    assert exporters.clock_timestamp(3661.5) == "01:01:01"


def test_srt_structure():
    out = exporters.to_srt(SEGMENTS)
    assert out.startswith("1\n00:00:00,000 --> 00:00:02,500\nKumusta, are you okay?\n\n")
    assert "\n2\n00:00:02,500 --> 00:00:04,000\n" in out


def test_vtt_has_header():
    assert exporters.to_vtt(SEGMENTS).startswith("WEBVTT\n\n")


def test_txt_with_and_without_timestamps():
    assert exporters.to_txt(SEGMENTS).startswith("[00:00:00] Kumusta")
    plain = exporters.to_txt(SEGMENTS, include_timestamps=False)
    assert plain == "Kumusta, are you okay?\nOo naman, I'm fine.\n"


def test_overlapping_and_negative_cues_are_normalised():
    messy = [
        {"start": -1.0, "end": 2.0, "text": "one"},
        {"start": 1.0, "end": 0.5, "text": "two"},
        {"start": 5.0, "end": 6.0, "text": "   "},
    ]
    out = exporters.to_srt(messy)
    assert "00:00:00,000 --> 00:00:02,000" in out
    assert "00:00:02,000 --> 00:00:02,050" in out
    assert out.count("-->") == 2


def test_safe_filename():
    assert exporters.safe_filename("memo: 2026/09/21", "srt") == "memo_ 2026_09_21.srt"
    assert exporters.safe_filename("///", "txt") == "transcript.txt"
