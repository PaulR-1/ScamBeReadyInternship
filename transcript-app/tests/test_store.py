def test_queue_claim_and_finish(db, transcript_id):
    claimed = db.claim_next_queued()
    assert claimed["id"] == transcript_id
    assert claimed["status"] == "running"
    assert db.claim_next_queued() is None

    db.finish_transcript(transcript_id, "completed")
    row = db.get_transcript(transcript_id)
    assert row["status"] == "completed"
    assert row["progress"] == 1.0


def test_interrupted_rows_are_recovered(db, transcript_id):
    db.claim_next_queued()
    assert db.mark_running_as_interrupted() == 1
    assert db.get_transcript(transcript_id)["status"] == "interrupted"


def test_segment_edit_and_revert(db, transcript_id):
    db.add_segments(transcript_id, [{"idx": 0, "start": 0.0, "end": 1.0, "text": "orihinal"}])
    segment = db.get_segments(transcript_id)[0]
    assert segment["edited"] == 0

    edited = db.update_segment_text(segment["id"], "edited na")
    assert edited["text"] == "edited na"
    assert edited["original_text"] == "orihinal"
    assert edited["edited"] == 1

    reverted = db.revert_segment(segment["id"])
    assert reverted["text"] == "orihinal"
    assert reverted["edited"] == 0


def test_editing_back_to_original_clears_the_flag(db, transcript_id):
    db.add_segments(transcript_id, [{"idx": 0, "start": 0.0, "end": 1.0, "text": "same"}])
    segment_id = db.get_segments(transcript_id)[0]["id"]
    db.update_segment_text(segment_id, "changed")
    assert db.update_segment_text(segment_id, "same")["edited"] == 0


def test_requeue_clears_segments_and_state(db, transcript_id):
    db.claim_next_queued()
    db.add_segments(transcript_id, [{"idx": 0, "start": 0.0, "end": 1.0, "text": "hi"}])
    db.finish_transcript(transcript_id, "failed", "boom")

    db.requeue(transcript_id)
    row = db.get_transcript(transcript_id)
    assert row["status"] == "queued"
    assert row["error"] is None
    assert row["progress"] == 0.0
    assert row["model"] == "large-v3"
    assert db.get_segments(transcript_id) == []


def test_requeue_applies_changed_settings(db, transcript_id):
    db.finish_transcript(transcript_id, "failed", "boom")
    db.requeue(transcript_id, model="medium", language="auto")

    row = db.get_transcript(transcript_id)
    assert row["model"] == "medium"
    assert row["language"] == "auto"
    assert row["initial_prompt"] == "Taglish prompt"


def test_cancel_flag_only_applies_to_active_jobs(db, transcript_id):
    db.request_cancel(transcript_id)
    assert db.is_cancel_requested(transcript_id) is True

    db.finish_transcript(transcript_id, "completed")
    db.requeue(transcript_id)
    assert db.is_cancel_requested(transcript_id) is False


def test_settings_round_trip(db):
    db.save_settings({"language": "auto", "beam_size": "1"})
    settings = db.get_settings()
    assert settings["language"] == "auto"
    assert settings["beam_size"] == "1"
    assert settings["model"] == "large-v3"


def test_delete_removes_segments(db, transcript_id):
    db.add_segments(transcript_id, [{"idx": 0, "start": 0.0, "end": 1.0, "text": "hi"}])
    db.delete_transcript(transcript_id)
    assert db.get_transcript(transcript_id) is None
    assert db.get_segments(transcript_id) == []
