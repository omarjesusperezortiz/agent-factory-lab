# Handoff 2026-10-23: MacBook session → Mac mini

## State

- **Dashboard tabs** (Ticket flow through Research notes): Console/Traces/Issues mock, Ticket flow, Harness playbook, Dev setup, RAG & context, Teams & supervision, Iceberg (30), Spec-driven, Orchestration, Be ambitious, Research notes, OpenTelemetry.
- **Published:** the Artifact (v21) and GitHub Pages are in sync with `src/dashboard.html`.
- **Skills:**
  - `visual-explainer` is a user skill. On the Mini it is at `~/.claude/skills/visual-explainer`, and a workspace copy is at `~/projects/learning-heroes/learning-heroes-ai/skills/visual-explainer` (uncommitted there).
  - The `watch` plugin (bradautomates/claude-video) must be installed per machine:
    1. `/plugin marketplace add bradautomates/claude-video`
    2. `/plugin install watch@claude-video`
    3. Set it to the local engine and leave `GEMINI_API_KEY` unset.

## Decisions already made

- **Orchestration:** the ticket ledger and the dispatch loop stay in plain code (`decisions/0001`). Not on agent teams. Learn from Gas Town without installing it.
- **Spec format:** OpenSpec's file format for our pipeline. Use an `sdd` flag per ticket, and archive on merge.
- **Tickets get an `outcome` field** (altitude), and the reviewer runs on a different model (outside judge).

## Open: waiting on the user

1. **Knowledge & handoff tab.** It is built (`private/know.*`). It contains an anonymized case study of a work repo. Options: artifact only (recommended), both, or skip.
2. **Videos feed.** Plan below. Needs (a) the list of channels besides AI Labs, and (b) whether updates arrive as a PR to review (recommended) or go straight to the site.

## Planned: videos feed + daily job

- **Site:** `/videos/` is a blog-style feed: newest first, cards, tags. Each video gets a page at `/videos/<date>-<slug>/`.
  - Data source: `videos/index.json`. Fields: id, channel, date, title, summary, tags, relevance score 0–5, page path.
  - The feed renders that file.
- **Job:** launchd on this Mac mini, daily. Not GitHub Actions, because YouTube blocks its runners and it would need an API key.
  1. **Find new videos:** read each channel's RSS (`https://www.youtube.com/feeds/videos.xml?channel_id=…`) and diff it against `index.json`.
  2. **Summarise every new video:** transcript only, run through `claude -p`, giving a summary, tags and a score.
  3. **Score ≥ 4:** build a full visual explainer with the `visual-explainer` skill.
  4. **Publish:** commit on a branch and open a PR with `gh`. The user merges.
- **Lesson from the Mini's old prod-signup-monitor:** an unattended `claude -p` cannot use OAuth MCP connectors. Use plain CLIs only (`gh`, `yt-dlp`, `curl`).

## Done in this session, for reference

- Research tabs: Orchestration (9 ways × 6 jobs, worker-crash simulation) and Be ambitious (6 scenes redrawn from the AI Labs video's motion graphics).
- Mac mini SSH: `ssh omarjesusperezortiz@100.110.82.11` (Tailscale, by IP).
