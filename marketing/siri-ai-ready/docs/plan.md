# "Get your apps ready for Siri AI" video: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Three finished 1080×1920 versions of one ~52 s video (HyperFrames, HeyGen presenter, Chrome recording) that
share one narration, one LTX opening shot and the voiced Wikipedia clip.

**Architecture:** Shared assets are made once in `videos/siri-ai-ready/shared/`. Each version builds from them in its
own folder and ends as one mp4. A single checker script (`check.py`) is the test every task runs against its output.

**Tech Stack:** HeyGen CLI (TTS, avatar video), a local LTX cutscene tool (LTX-2.5 on Daytona), HyperFrames CLI,
Chrome 157 over the DevTools protocol (Node, `puppeteer-core`), ffmpeg/ffprobe, Python 3 for checks.

**Spec:** `docs/design.md`

## Global Constraints

- 1080×1920, H.264 + AAC, 40–52 s.
- Captions burned in.
- Voice: HeyGen "Joanna – Warm & Conversational", `776f9d2ff401499a8f1f2bcb4ca46004`, en-US. No "Hey Siri" in any audio.
- Script, on-screen text and timings exactly as the spec's Script table (including the README's three "5 of 5" lines
  labelled as sample tools, and `npx expo install expo-syrup-ai-kit expo-app-intents`).
- End-card small print, verbatim: "Not affiliated with or endorsed by Apple. Siri and iPhone are trademarks of Apple
  Inc., registered in the U.S. and other countries and regions." and "Example built on Wikipedia's open-source iOS app.
  Not affiliated with the Wikimedia Foundation."
- No Apple logos, Apple typefaces or Siri look on our cards; no generated phones; no private footage.
- Deliverables: `siri-ai-ready-{a-hyperframes,b-heygen,c-chrome}.mp4`.
- HeyGen: check the estimate before submitting B; stop and ask if one take would use more than 100 of the 402 credits.
- The working folder was not a git repo: there are no commits. Each task ends with its check passing instead.
- Daytona: delete every sandbox the LTX run creates; confirm none are left.

## Review Focus

1. Captions drifting from the voice → each caption's start must be within 0.15 s of its first word's timestamp
   (Task 1 test `captions_match_words`).
2. The Wikipedia clip's 2008→1920 crop cutting off Siri's reply card at the top or the highlight → check frames at the
   reply (clip 5 s) and the highlight (clip 10 s) keep both visible (Task 4 visual check, recorded in the ledger).
3. HTML-in-Canvas drawing before the first paint, giving blank sheets → `check.py --not-blank` on frames from each
   effect scene (Task 3).
4. Loudness jump between narration and the clip's question → whole-video integrated loudness −16 ±1 LUFS and the
   clip's segment within 2 LU of the narration (`check.py` loudness test, every version).
5. Version C's capture not being 1080×1920 or dropping frames → `check.py` dimension and frame-count tests on C's raw
   capture (Task 5).

---

### Task 1: Shared narration, timings and checker

**Files:**
- Create: `videos/siri-ai-ready/check.py`, `videos/siri-ai-ready/test_check.py`
- Create: `videos/siri-ai-ready/shared/lines.json` (the six narration lines from the spec, ids `hook`, `why`, `package`,
  `tests`, `wiki`, `close`)
- Create: `videos/siri-ai-ready/shared/narration/<id>.mp3`, `shared/timeline.json`, `shared/captions.json`

**Interfaces:**
- Produces: `check.py <mp4> [--not-blank t1,t2,…]` exits 0 when the file is 1080×1920, H.264+AAC, 40–52 s, −16 ±1 LUFS,
  and (with `--not-blank`) the frames at those times aren't flat colour; prints one line per failed check.
- Produces: `timeline.json`: `[{id, start_s, end_s, file}]`, narration placed at the spec's times; the clip at 28.0 s.
- Produces: `captions.json`: `[{start_s, end_s, text}]`, built from HeyGen word timestamps, at most 5 words per caption.

- [ ] **Step 1: Write `test_check.py`** with `test_rejects_wrong_size` (a 1080×1080 2 s colour clip made with ffmpeg →
  exit 1, output contains "size"), `test_rejects_blank_frame` (a flat colour frame with `--not-blank 1` → exit 1),
  `test_accepts_good_file` (a 1080×1920 45 s clip with −16 LUFS tone → exit 0), and `captions_match_words` (every
  caption start within 0.15 s of its first word's `start` in the HeyGen response saved next to each mp3).
- [ ] **Step 2: Run** `python3 -m pytest videos/siri-ai-ready/test_check.py -q` → fails (no `check.py`, no captions).
- [ ] **Step 3: Implement `check.py`** with ffprobe (size, codecs, duration), ffmpeg `ebur128` (loudness) and
  `signalstats` YDIF/YAVG range (blank frames).
- [ ] **Step 4: Generate narration**: one `heygen voice speech create` per line with Joanna, `--locale en-US`, keeping
  each JSON response (`<id>.json`) for the word timestamps; then write `timeline.json` and `captions.json`.
  If a line runs past its slot, re-generate it at `--speed 1.05`–`1.1`, never faster.
- [ ] **Step 5: Run** the tests → pass. Record each line's duration in the ledger.

### Task 2: LTX opening shot

**Files:**
- Create: `videos/siri-ai-ready/shared/opening/still.png` (896×1536), `prompt.txt`, `seed-<n>.mp4`, `opening.mp4`
  (1080×1920, 5 s, no audio)

**Interfaces:**
- Consumes: a local LTX cutscene tool (`npm run cutscene` with `LTX_PROMPT`, `LTX_START_IMAGE`, `LTX_SECONDS=5`,
  `LTX_WIDTH=896`, `LTX_HEIGHT=1536`, `LTX_SEED`, `LTX_OUTPUT`) and `DAYTONA_API_KEY` read from
  a local `.env` file (never printed or copied).
- Produces: `shared/opening/opening.mp4`.

- [ ] **Step 1:** Make `still.png`: a desk-top scene of 6–8 generic rounded app icons in our colours (no Apple glyphs),
  the top third left empty for the hook text, rendered from a small HTML page with headless Chrome.
- [ ] **Step 2:** Run three seeds (`7`, `42`, `1234`) one after another; keep each log next to its mp4.
- [ ] **Step 3:** Confirm no Daytona sandboxes are left (list via the SDK in that tool); expected: none from this run.
- [ ] **Step 4:** Make a contact sheet of each seed (1 frame/s) and pick the one with no warped icons, no phone shapes,
  no text-like glyphs; ledger the pick and why. Scale it to 1080×1920 → `opening.mp4`.

### Task 3: Version A, HyperFrames

**Files:**
- Create: `videos/siri-ai-ready/a-hyperframes/` (HyperFrames project: `index.html`, scenes, `assets/` linking the shared
  files)
- Create: `videos/siri-ai-ready/siri-ai-ready-a-hyperframes.mp4`

**Interfaces:**
- Consumes: Task 1 `timeline.json`, `captions.json`, narration; Task 2 `opening.mp4`;
  `footage/answer-links/eiffel-siri-opens-at-answer-voiced.mp4`.
- Produces: the scene HTML (one file per scene: `hook`, `why`, `package`, `tests`, `close`) that Task 5 reuses.

- [ ] **Step 1: Spike the flag.** A one-scene composition whose canvas calls `drawElementImage` inside `onpaint`;
  render 2 s with the renderer's Chrome launched with `--enable-blink-features=CanvasDrawElement` (find how the CLI
  passes browser flags; if it can't, try `--browser-path` to Chrome 157). Run `check.py --not-blank 1`.
  Ledger the result. If neither works, build the effect scenes with CSS 3D and say so.
- [ ] **Step 2:** Build the scenes to the spec's Script table: hook over `opening.mp4`; the "now / spring" card; the
  README Swift snippet and `siri-tools.json` as folding sheets; the three labelled "5 of 5" lines printing out; the
  voiced clip centre-cropped to 1920; the end card with the install command, package URL, repo and both small-print
  lines. Captions from `captions.json`.
- [ ] **Step 3:** `npx hyperframes check` (lint/validate) → clean.
- [ ] **Step 4:** Render 1080×1920 → `siri-ai-ready-a-hyperframes.mp4`; run
  `check.py … --not-blank 2,10,16,24,46` → exit 0. Contact sheet at 1 frame/s reviewed for Review Focus 2.

### Task 4: Version B, HeyGen presenter

**Files:**
- Create: `videos/siri-ai-ready/b-heygen/request.json`, `avatar.mp4`, `siri-ai-ready-b-heygen.mp4` (in the parent folder)

**Interfaces:**
- Consumes: Task 1 narration (concatenated to one `narration.mp3` on the timeline, minus the clip's span), Task 2
  `opening.mp4`, Task 3 scene renders for the inserts (`package`, `tests`, `close` as standalone mp4s).

- [ ] **Step 1:** List avatars (`heygen avatar list`), shortlist three whose look suits Joanna's voice, and ledger them;
  pick the first unless the user names another.
- [ ] **Step 2:** Get the estimate for a vertical 1080×1920 avatar video lip-synced to `narration.mp3` (audio upload via
  `heygen asset`, then `heygen video create` with the recorded track). If over 100 credits, stop and ask.
- [ ] **Step 3:** Create it with `--wait`; download `avatar.mp4`.
- [ ] **Step 4:** Composite with ffmpeg: opening full-frame under the hook, avatar for `why`, inserts picture-in-picture
  for `package`/`tests` (avatar in the lower third), the voiced clip full-frame, end card full-frame; captions burned in.
- [ ] **Step 5:** `check.py siri-ai-ready-b-heygen.mp4 --not-blank 6,15,24,46` → exit 0; contact sheet reviewed.

### Task 5: Version C, live Chrome recording

**Files:**
- Create: `videos/siri-ai-ready/c-chrome/page.html` (self-playing, the Task 3 scenes on a timer, HTML-in-Canvas on),
  `record.mjs`, `capture.mp4`, then `siri-ai-ready-c-chrome.mp4` (parent folder)

**Interfaces:**
- Consumes: Task 3 scene HTML; Task 1 narration and captions; Task 2 opening; the voiced clip.
- Produces: `record.mjs --url <file> --seconds 52 --out capture.mp4`: launches
  `/Applications/Google Chrome.app/…/Google Chrome` headless with a 1080×1920 viewport at `deviceScaleFactor: 1`,
  captures with `Page.startScreencast` (or `HeadlessExperimental.beginFrame` if screencast drops frames) and encodes
  at 30 fps.

- [ ] **Step 1:** Write `record.mjs`; run it on a 3 s test page; `check.py`-style probe: 1080×1920, 90 ±2 frames.
- [ ] **Step 2:** Record `page.html` → `capture.mp4`; probe frame count 1560 ±30.
- [ ] **Step 3:** Mux with the narration and the clip's audio (the clip's video is inside the page) → final mp4.
- [ ] **Step 4:** `check.py siri-ai-ready-c-chrome.mp4 --not-blank 2,10,16,24,46` → exit 0; contact sheet reviewed.

### Task 6: Hand-over

- [ ] **Step 1:** Run `check.py` on all three finals → all exit 0.
- [ ] **Step 2:** Review one frame per second of each final for private content and Apple look; ledger "clean".
- [ ] **Step 3:** Add the three videos to `video-shotlist.md` under Footage, with what each is and how it was made.
- [ ] **Step 4:** Delete working files that aren't inputs to a final (seed clips not picked, spike output); stop any
  process started; confirm no Daytona sandboxes remain.
- [ ] **Step 5:** Send the three videos to the user.
