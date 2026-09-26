# agent-docs

Shared, durable knowledge for every agent and contributor working in this repository.
Anything an agent would otherwise have to rediscover by reading the whole codebase belongs here.

## Index

| File | Read it when |
| --- | --- |
| [project-brief.md](project-brief.md) | You need the goal, scope, and non-goals of the transcription app. |
| [environment.md](environment.md) | You need the target machine's hardware, installed tooling, and setup steps. |
| [architecture.md](architecture.md) | You are changing how components fit together or adding a module. |
| [conventions.md](conventions.md) | You are writing code, naming things, or adding dependencies. |
| [taglish-notes.md](taglish-notes.md) | You are touching transcription quality, prompts, or language settings. |
| [decisions.md](decisions.md) | You want to know why something is the way it is, before changing it. |
| [status.md](status.md) | You are starting or finishing a work session. |

## How to use this folder

- **Before work:** read `project-brief.md`, `architecture.md`, and `status.md` at minimum.
- **During work:** if you make a choice a future agent could reasonably reverse by accident,
  add it to `decisions.md` with the reasoning and the tradeoff.
- **After work:** append to `status.md` — what changed, what is verified, what is still open.

## Rules for editing this folder

- Keep documents short and factual. No marketing language, no speculation presented as fact.
- If a statement here contradicts the code, the code wins — fix the document in the same change.
- Do not delete entries from `decisions.md`; supersede them with a new dated entry instead.
