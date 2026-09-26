import pytest

from app.services import media


def test_blank_path_is_rejected():
    with pytest.raises(media.MediaError, match="Enter the full path"):
        media.resolve_source("   ")


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(media.MediaError):
        media.resolve_source(str(tmp_path / "nope.mp3"))


def test_directory_is_rejected(tmp_path):
    with pytest.raises(media.MediaError):
        media.resolve_source(str(tmp_path))


def test_unsupported_extension_is_rejected(tmp_path):
    doc = tmp_path / "notes.txt"
    doc.write_text("hello")
    with pytest.raises(media.MediaError, match="not a supported format"):
        media.resolve_source(str(doc))


def test_quoted_path_from_windows_copy_as_path(tmp_path):
    audio = tmp_path / "memo.m4a"
    audio.write_bytes(b"x")
    assert media.resolve_source(f'"{audio}"') == audio.resolve()


def test_cleanup_is_safe_on_missing_file(tmp_path):
    media.cleanup(tmp_path / "gone.wav")
    media.cleanup(None)


def test_guess_media_kind(tmp_path):
    assert media.guess_media_kind(tmp_path / "a.mp4") == "video"
    assert media.guess_media_kind(tmp_path / "a.m4a") == "audio"
