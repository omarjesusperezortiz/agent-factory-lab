#!/bin/bash
# Daily video feed. Run by ~/Library/LaunchAgents/com.omar.video-feed.plist (see scripts/com.omar.video-feed.plist).
# Works in its own clone, so the job never touches the checkout a person is editing.
# Publishes straight to main: GitHub Pages serves the feed at /videos/.
set -uo pipefail

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
FEED_DIR="${FEED_DIR:-$HOME/projects/agent-factory-lab-feed}"
REPO_URL="git@github.com:omarjesusperezortiz/agent-factory-lab.git"
LOG="$HOME/Library/Logs/video-feed.log"

# Optional: CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`) if the keychain login isn't reachable from launchd.
[ -f "$HOME/.video-feed.env" ] && { set -a; . "$HOME/.video-feed.env"; set +a; }

exec >>"$LOG" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') video-feed start"
fail() { echo "FAILED: $1"; osascript -e "display notification \"$1\" with title \"video-feed failed\"" >/dev/null 2>&1; exit 1; }

[ -d "$FEED_DIR/.git" ] || git clone -q "$REPO_URL" "$FEED_DIR" || fail "clone"
cd "$FEED_DIR" || fail "cd $FEED_DIR"
git checkout -q main && git fetch -q origin && git reset -q --hard origin/main || fail "sync with origin/main"

python3 scripts/video_feed.py
status=$?

if [ -n "$(git status --porcelain videos)" ]; then
  git add videos
  git commit -q -m "Video feed: $(date +%Y-%m-%d)" || fail "commit"
  git pull -q --rebase origin main && git push -q origin main || fail "push"
  echo "pushed $(git rev-parse --short HEAD)"
else
  echo "no new videos"
fi

[ "$status" -eq 0 ] || fail "some videos failed, see $LOG"
echo "=== done"
