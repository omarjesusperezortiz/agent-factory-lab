# agent-factory-lab

Research on orchestrating AI coding agents into a software factory. Public repo, published on GitHub Pages:
https://omarjesusperezortiz.github.io/agent-factory-lab/

## Layout

The site has three parts. Edit the sources in `src/`, never the built `index.html` files.

| URL | Source | What it is |
|---|---|---|
| `/` | `src/landing.html` (full page) | 3D scroll landing (Three.js + GSAP ScrollTrigger) ending at two doors: Console and Research |
| `/console/` | `src/console.html` (fragment) | Mockup of how the factory will run: Console, Traces, Issues, Human inbox, Evals, Prompts, Costs |
| `/research/` | `src/research.html` (fragment) | Blog: home with posts and the video feed, one post per research topic, explainers at `#videos/<folder>` |

- `./build.sh` copies the landing and wraps the two fragments into `console/index.html` and `research/index.html`. Run it before every commit.
- The landing redirects old dashboard links (`/#orch`, `/#console`…) to `/research/` or `/console/`.
- **The console is also a private claude.ai Artifact:** https://claude.ai/artifact/Bws2CJPVkzxv91UvDupScq (Learning Heroes account)
  - From a new session, read it with the Artifact tool first.
  - Then publish `src/console.html` with that `url` so the link stays the same.
- `research/thumbs/<post-id>.jpg`: YouTube-style post thumbnails (1280×720, a few big words over a zoomed piece of the post's own diagram). Template: `scripts/thumbs/card.html?img=…&k=kicker&t=Title%20<em>word</em>&c=%23accent&pos=…&w=…`, screenshotted at 1280×720.
- `research/sources.md`, `research/videos.md`: source lists. `decisions/`: one file per decision. `handoffs/`: session handoffs, newest first.
- `videos/`: data for the research blog's video feed. `index.json` is the feed, `channels.txt` lists followed channels, `<date>-<slug>/index.html` is a standalone explainer.
  - The blog opens an explainer at `research/#videos/<date>-<slug>` in a frame and removes its `<nav class="top">`. `videos/index.html` only redirects to `../research/#videos`.
  - Filled daily at 08:00 by `scripts/video-feed.sh` (launchd agent `com.omar.video-feed`, template in `scripts/`). It runs in its own clone at `~/projects/agent-factory-lab-feed` and pushes straight to `main`.
  - Log: `~/Library/Logs/video-feed.log`. Run now: `launchctl kickstart gui/$(id -u)/com.omar.video-feed`.
- `private/`: gitignored. Material from work or company repos lives there and never goes into the public site without the user's explicit yes.

## How the pages are built

- **Research post:** a `<section class="view doc" id="v-NAME" hidden>` in `src/research.html`, before `<nav class="rs-next"`.
  - Add `['NAME', 'Category']` to `POSTS`, newest first; the first three are featured on the home page. Title and summary come from the post's `<h1>` and `.lede`.
  - Give it a thumbnail at `research/thumbs/NAME.jpg`.
  - Its script goes in its own IIFE that returns early when its elements are missing.
- **Console view:** a `<section class="view" id="v-NAME" hidden>` in `src/console.html`, registered in `VIEW_NAMES` with a sidebar link `href="#NAME"`.
- **Class names:** never use a bare short class (`.run`, `.btn`, `.v2`, `.st`…) inside a stage: the shared stylesheet already styles them globally. Prefix every one.
- **Moving markup between files:** cut a section by matching opening and closing tags, never by searching for the first `</section>`.
- **Prefixes:** every view's CSS and JS uses a unique prefix (`.sp-`, `.or-`, `.rs-`, `.vd-`, `.lp-`…). Global classes like `.warn` clash.
- **Animated explainers:** use the `visual-explainer` skill.
  - Derive the visuals from the source (video frames, the essay's own metaphors).
  - Never reuse an earlier tab's stage.
  - Decide the layout yourself; don't ask the user to pick.
- **Verify in Chrome before publishing:** run every scene at ~1470px and at 400px (no horizontal scroll), then check the console.

## Working rules

- Commit messages end with the Co-Authored-By line the session gives.
- Follow up on research with markdown-linked sources.
