#!/usr/bin/env python3
"""Daily video feed: find new videos, summarise them, build explainers for the best.

Run from the repo root (scripts/video-feed.sh does that). Plain CLIs only: an
unattended `claude -p` cannot log in to OAuth connectors, so everything here is
curl-style HTTP, yt-dlp and claude with no MCP.
"""
import json, os, re, subprocess, sys, tempfile, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path.cwd()
INDEX = ROOT / 'videos' / 'index.json'
CHANNELS = ROOT / 'videos' / 'channels.txt'
MAX_AGE_DAYS = int(os.environ.get('FEED_MAX_AGE_DAYS', 14))  # ignore older uploads, so a new channel doesn't flood the feed
MAX_NEW = int(os.environ.get('FEED_MAX_NEW', 5))
MAX_EXPLAINERS = int(os.environ.get('FEED_MAX_EXPLAINERS', 1))
SUMMARY_MODEL = os.environ.get('FEED_SUMMARY_MODEL', 'claude-sonnet-5-5')
EXPLAINER_MODEL = os.environ.get('FEED_EXPLAINER_MODEL', 'claude-opus-5-5')
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}


def log(msg):
    print(f'[{datetime.now():%H:%M:%S}] {msg}', flush=True)


def channel_ids():
    for line in CHANNELS.read_text().splitlines():
        line = line.split('#', 1)[0].strip()
        if line:
            yield line


def fetch_feed(channel_id):
    url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'video-feed/1'}), timeout=30) as r:
        root = ET.fromstring(r.read())
    channel = root.findtext('a:title', '', NS)
    for e in root.findall('a:entry', NS):
        yield {
            'id': e.findtext('yt:videoId', '', NS),
            'channel': channel,
            'published': datetime.fromisoformat(e.findtext('a:published', '', NS)),
            'title': e.findtext('a:title', '', NS),
            'description': e.findtext('media:group/media:description', '', NS),
        }


def transcript(video_id, tmp):
    """Captions as plain text, or '' when the video has none."""
    subprocess.run(['yt-dlp', '--skip-download', '--write-subs', '--write-auto-subs',
                    '--sub-langs', 'en-orig,en,es-orig,es', '--sub-format', 'vtt',
                    '-o', f'{tmp}/%(id)s.%(ext)s', f'https://www.youtube.com/watch?v={video_id}'],
                   capture_output=True, text=True, timeout=300)
    for lang in ('en-orig', 'en', 'es-orig', 'es'):
        f = Path(tmp) / f'{video_id}.{lang}.vtt'
        if f.exists():
            out, last = [], None
            for line in f.read_text(errors='ignore').splitlines():
                if not line.strip() or '-->' in line or line.startswith(('WEBVTT', 'Kind:', 'Language:')):
                    continue
                line = re.sub(r'<[^>]+>', '', line).strip()
                if line and line != last:  # auto-captions repeat each line as they roll
                    out.append(line)
                    last = line
            return ' '.join(out)
    return ''


def claude(prompt, *args, timeout=600):
    r = subprocess.run(['claude', '-p', *args], input=prompt, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f'claude exited {r.returncode}: {(r.stderr or r.stdout)[-500:]}')
    return r.stdout


SUMMARY_PROMPT = """You curate a research feed for agent-factory-lab: research on orchestrating AI coding agents into a software factory (ticket pipelines, Claude Code, specs, harnesses, evals, multi-agent orchestration, context and memory, review loops).

Read this YouTube video's transcript and reply with ONLY a JSON object, no prose, no code fence:
{{"summary": "2-3 plain sentences: what the video claims and the one idea worth keeping", "tags": ["3-5 lowercase-kebab tags"], "score": 0-5, "slug": "3-6-word-kebab-slug"}}

Score = relevance to the lab: 5 changes how we'd build the factory, 4 a concrete technique we could adopt, 3 useful background, 2 tangential, 0-1 off-topic or pure promotion.

Title: {title}
Channel: {channel}
Transcript ({source}):
{text}
"""

EXPLAINER_PROMPT = """Use the visual-explainer skill to build an animated explainer of this YouTube video: https://www.youtube.com/watch?v={id}
Title: {title}

This is an unattended run. Rules for this run:
- Write ONE self-contained page to {out}/index.html (copy the skill's template.html as the start). No other files outside {out}/.
- Use the watch skill with the local engine for frames and transcript; put temporary files under {tmp}.
- Do not open a browser, publish an Artifact, edit other files, or run git. The calling script commits.
- Add a link back to the feed (`../`) and to the video at the top of the page.
"""


def summarise(v, tmp):
    text = transcript(v['id'], tmp)
    source = 'captions' if text else 'no captions, video description only'
    out = claude(SUMMARY_PROMPT.format(title=v['title'], channel=v['channel'], source=source,
                                       text=(text or v['description'])[:60000]),
                 '--model', SUMMARY_MODEL, '--tools', '')
    m = re.search(r'\{.*\}', out, re.S)
    if not m:
        raise RuntimeError(f'no JSON in summary output: {out[:300]}')
    data = json.loads(m.group(0))
    return {
        'id': v['id'], 'channel': v['channel'], 'date': v['published'].date().isoformat(), 'title': v['title'],
        'summary': data['summary'].strip(), 'tags': [t.lower() for t in data.get('tags', [])][:5],
        'score': max(0, min(5, int(data['score']))), 'page': None,
        'slug': re.sub(r'[^a-z0-9-]+', '-', data.get('slug', v['id']).lower()).strip('-')[:60] or v['id'],
        'transcript': bool(text),
    }


def build_explainer(row, tmp):
    folder = f"{row['date']}-{row['slug']}"
    out = ROOT / 'videos' / folder
    out.mkdir(parents=True, exist_ok=True)
    claude(EXPLAINER_PROMPT.format(id=row['id'], title=row['title'], out=out, tmp=tmp),
           '--model', EXPLAINER_MODEL, '--permission-mode', 'acceptEdits', '--max-budget-usd', '8',
           '--allowedTools', 'Skill', 'Read', 'Write', 'Edit', 'Glob', 'Grep',
           'Bash(yt-dlp:*)', 'Bash(ffmpeg:*)', 'Bash(ffprobe:*)', 'Bash(python3:*)', 'Bash(mkdir:*)', 'Bash(ls:*)', 'Bash(cp:*)',
           timeout=3600)
    if not (out / 'index.html').exists():
        raise RuntimeError(f'explainer run finished without writing {out}/index.html')
    return f'{folder}/'


def main():
    rows = json.loads(INDEX.read_text())
    seen = {r['id'] for r in rows}
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    new = []
    for cid in channel_ids():
        try:
            new += [v for v in fetch_feed(cid) if v['id'] not in seen and v['published'] >= cutoff]
        except Exception as e:
            log(f'feed {cid} failed: {e}')
    new.sort(key=lambda v: v['published'])
    log(f'{len(new)} new video(s); processing up to {MAX_NEW}')

    failures, explainers = 0, 0
    with tempfile.TemporaryDirectory(prefix='video-feed-') as tmp:
        for v in new[:MAX_NEW]:
            try:
                row = summarise(v, tmp)
                log(f"summarised {v['id']} score={row['score']} {v['title']!r}")
            except Exception as e:
                failures += 1
                log(f"summary failed for {v['id']}: {e}")
                continue
            if row['score'] >= 4 and explainers < MAX_EXPLAINERS:
                try:
                    row['page'] = build_explainer(row, tmp)
                    explainers += 1
                    log(f"explainer built at videos/{row['page']}")
                except Exception as e:
                    failures += 1
                    log(f"explainer failed for {v['id']}: {e}")
            rows.append(row)
            INDEX.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')  # save after each video so a crash keeps earlier work
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
