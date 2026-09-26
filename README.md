# ScamBeReadyInternship

Two local tools in one repo.

**Taglish Transcriber** (`transcript-app/`) turns voice memos and videos into editable transcripts on your own laptop. It is built for Taglish (Tagalog mixed with English) and does not upload audio. See `transcript-app/README.md` to install and run it.

**Partner scraper** (`scraper/`) collects possible Manila university contacts for Be Scam Ready. Run it with:

```powershell
pip install -r requirements.txt
python -m scraper
```

Collected contact files in `data/` stay on your machine and are not part of this repository.
