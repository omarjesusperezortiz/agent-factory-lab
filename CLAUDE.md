# agent-factory-lab

Research on orchestrating AI coding agents into a software factory. Public repo, published on GitHub Pages:
https://omarjesusperezortiz.github.io/agent-factory-lab/

## Layout

- `src/dashboard.html`: the dashboard source. Edit this file, never `index.html`.
- `./build.sh`: wraps the source into `index.html` for GitHub Pages. Run it before every commit.
- **The same source is also a private claude.ai Artifact:** https://claude.ai/artifact/VuqFn39k8otRnaSJihfQCK
  - From a new session, read it with the Artifact tool first.
  - Then publish `src/dashboard.html` with that `url` so the link stays the same.
- `research/`: sources and videos. `decisions/`: one file per decision. `handoffs/`: session handoffs, newest first.
- `private/`: gitignored. Material from work or company repos lives there and never goes into the public site without the user's explicit yes.

## How the dashboard is built

- **Views:** each view is `<section class="view doc" id="v-NAME" hidden>`.
  - Register it in `VIEW_NAMES`.
  - Add a sidebar link with `href="#NAME"`.
  - Insert the view before `<!-- ============ RESEARCH NOTES ============ -->`.
- **Prefixes:** every view's CSS and JS uses a unique prefix (`.sp-`, `.or-`, `.v2`…). Global classes like `.warn` clash.
- **Animated explainers:** use the `visual-explainer` skill.
  - Derive the visuals from the source (video frames, the essay's own metaphors).
  - Never reuse an earlier tab's stage.
  - Decide the layout yourself; don't ask the user to pick.
- **Verify in Chrome before publishing:** run every scene at ~1470px and at 400px (no horizontal scroll), then check the console.

## Working rules

- Commit messages end with the Co-Authored-By line the session gives.
- Follow up on research with markdown-linked sources.
