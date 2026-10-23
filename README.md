# agent-factory-lab

Research on orchestrating AI coding agents into a software factory. The working pipeline is:

orchestrator → scout/spec → human approval → worker → tester → final review

Open `index.html` in a browser. It is one self-contained page with no build step.

## Tabs

| Group | Tabs |
|---|---|
| Monitor (mock dashboard) | Console, Traces, Issues, Human inbox |
| Improve | Evals, Prompts, Costs |
| Research | Ticket flow, Harness playbook, Dev setup, RAG & context, Teams & supervision, Iceberg (30), Spec-driven, Orchestration, Research notes, OpenTelemetry |

## Layout

- `index.html`: the dashboard.
- `research/sources.md`: the links cited, grouped by topic.
- `research/videos.md`: videos watched, plus a to-watch list.
- `decisions/`: one short file per decision, with the reason behind it.

## Status

Research only; nothing in this repo runs agents yet. The next step is a `starter/` folder with a reference loop:
1. Poll GitHub Issues.
2. Run `claude -p` in a git worktree for each ticket.
3. Run a sweeper and a `spec_ready` human gate.

See `decisions/0001-ledger-in-code.md`.
