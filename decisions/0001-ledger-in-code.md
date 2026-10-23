# 0001: Keep the ticket ledger and dispatch loop in plain code

Date: 2026-10-23 · Status: accepted

## Problem

The orchestrator misses tickets. When the list of open work lives in an LLM's context, tickets disappear in three ways:
- the context gets compacted,
- the session crashes,
- or the model decides it is finished while work is still open.

## Decision

- **Ledger:** the tracker (GitHub Issues or Linear) is the source of truth, with these states:
  `pending → spec_ready → in_progress → testing → review → done`
- **Dispatch loop:** plain code polls the tracker, takes a lease on a ticket, and runs one headless agent call per stage (`claude -p` or the Agent SDK).
- **Isolation:** each ticket gets its own git worktree.
- **Handoff between stages:** stages pass files only, never chat history.
- **Sweeper:** finds rows whose heartbeat has gone stale and puts them back in the queue.
- **Human gates:** a person approves at `spec_ready` and at merge.

## Rejected for now

- **Claude Code agent teams.** The feature is experimental and only works in an interactive session. `/resume` does not restore in-process teammates, and the docs warn that task status can lag. Those are the same failure modes we are trying to fix.
- **Gas Town / Gas City.** The ideas are good: one supervisor with disposable workers, a merge queue, and a health watcher. The toolkit itself is alpha and costs too much for our scale.

## Revisit when

- **Crashed long runs become expensive:** move the loop into Temporal or LangGraph with a checkpointer.
- **Local machines become the bottleneck:** use cloud sandboxes such as Claude Managed Agents.
