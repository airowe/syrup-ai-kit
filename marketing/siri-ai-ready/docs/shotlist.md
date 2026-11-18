# Demo video: Wikipedia + Siri AI (draft)

Target: under 90 seconds, one journey, real footage. No Apple logos, and no imitation of Apple's typefaces or look on
our own cards. Show the real iPhone screen, not a drawing of one.

## Shots

| Time | Shot | Source |
|---|---|---|
| 0–5s | Title card: "Siri AI, answering from Wikipedia's own code." | Plain card, our colours |
| 5–25s | iPhone screen recording, mic on: "In Wikipedia, summarize the article about the Eiffel Tower." Siri answers: "The Eiffel Tower is a lattice tower on the Champ de Mars in Paris…" | Control Center > Screen Recording, microphone on |
| 25–44s | Answer link: a voice asks "In Wikipedia, how tall is the Eiffel Tower?", Siri replies, and Wikipedia opens the article scrolled to "330 metres (1,083" with it highlighted. Caption: "The answer opens in the app, at the answer." | `footage/answer-links/eiffel-siri-opens-at-answer-voiced.mp4`, as is |
| 44–56s | The tool's code, about 15 lines: `SummarizeArticleIntent` calling Wikipedia's own search and summary data controllers inside `tool.answer { … }`. Caption: "No new networking. It wraps the app's existing calls." | Xcode, large font, `Wikipedia/Code/SiriTools/WikipediaSiriTools.swift` |
| 56–66s | Second ask: "In Wikipedia, what happened on this day in history?" Cut after the first two events. Drop this shot if the day's events aren't usable. | iPhone screen recording |
| 66–78s | Terminal: `syrup-ai-eval summarize` on the device run. Caption: "Tested with Siri Evaluations on an iPhone: 5 of 5." Show the On This Day block. | Terminal, the run-3 result |
| 78–90s | End card: `npx expo install expo-syrup-ai-kit`, the Swift package line, and the repo URL. Small print: "Not affiliated with or endorsed by Apple. Siri and iPhone are trademarks of Apple Inc., registered in the U.S. and other countries and regions." | Plain card |

## Before recording

- Install the Debug build with `SIRI_AI_PREVIEW` from a local Wikipedia iOS fork. The outcome overlay only appears
  during evaluation runs, so it won't be in the footage.
- Ask Siri once off camera first, so any one-time prompt doesn't appear in the take.
- Pick a moment when the On This Day answer has no deaths in its first two events, or cut before them.
- Do Not Disturb on, full battery, and a clean status bar.

## Measured on the phone (iPhone 16 Pro, iOS 27.3 beta)

- On This Day: 5 of 5 on Nov 12 (run 3) and 5 of 5 on Nov 13 (run 4). Siri called the tool every run.
- Summarize the Eiffel Tower article: 3 of 3 complete runs on Nov 13 (run 4), 2 of 2 on Nov 12 (run 3). Apple's pass
  rate was 60% on Nov 13 because 2 runs recorded no tool call, though their outcome logs say "succeeded" and Siri read
  Wikipedia's summary.
- Answer links (find in article, Nov 14): Siri answered "330 metres (1,083 ft) tall" in all 6 runs, Wikipedia opened
  the article at the highlighted "330 metres (1,083" in all 6, and came forward from the home screen 3 of 3. Apple's
  harness scored 5 of the 6 runs before their results arrived, so only 1 run counts as complete; it passed.
- On Nov 13 the On This Day answer opened with a mass stabbing and the Paris attacks. Check the day's events before
  using that shot.

## Footage (footage/)

- `eiffel-tower-take.mp4`: 22.7 s, silent, cut from run 4. Wikipedia screen, Siri thinking, Siri's answer card, and
  the evaluation overlay changing from "Tool calls: none" to "succeeded". For its first ~6 s the status bar shows
  iOS's back-link to the app the run started from; crop the top or cover it with a title.
- `wiki-run4/`: the raw recordings of all 10 runs plus outcome logs. **Private: don't share as is.** The first ~15 s of
  `eiffel-tower-5-runs.mp4` show another app's screen with personal notes, and `on-this-day-5-runs.mp4` shows the
  home screen with apps and notification counts.
- `answer-links/eiffel-siri-opens-at-answer-voiced.mp4`: 18.6 s, with sound, cut from the Nov 14 home-screen run 3.
  Safe to share: the home screen and the evaluation's "Tool calls" bar are cut out. The voice is HeyGen's "Joanna – Warm
  & Conversational" (this project's voice, set in `.media/preferences.json`), asking from 0.5 to 3.6 s over a held
  frame of Wikipedia's Today page. Siri's reply card appears at about 4.9 s with no voice, then the article opens at the
  highlighted answer and holds to the end. No "Hey Siri", so it won't wake viewers' phones.
  - `answer-links/eiffel-siri-opens-at-answer.mp4`: the same take, silent, without the held opening (14.8 s).
  - `answer-links/question-joanna.mp3`: the spoken question on its own (3.4 s).
- These are harness recordings: Siri gets the question as typed text, so there is no voice and no spoken answer. The
  5–25 s hero shot still needs a take you record yourself, asking out loud with the microphone on.

## Social video: "Get your apps ready for Siri AI" (Nov 15)

**v4 (73.8 s, locked script; not yet rendered):** "Let's be honest: Siri hasn't been much help with your apps."
Then Apple's rebuild as Siri AI, now in developer preview, calling your app's tools "if you set them up right. Most
developers won't, at least for a while." Then Syrup AI Kit: smooth Siri adoption for developers, a richer experience for
users, an open-source repo added by hand or given to a coding agent as a plugin. Then the discovery skill
(siri-ai-discover) reading screens and the data layer and writing the Swift; "Set up right" tools with the requests
they open up; the Wikipedia example and phone clip; close "Syrup AI Kit. Get your apps ready for Siri AI." Syrup
effects: a pour wipe from the top into the package scene and into the close, a strip melt-in of the "Syrup AI Kit"
titles, and small drips under landing cards. The discovery shortlist uses an illustrative "Sample App". Built by
`videos/siri-ai-ready/shared/retime_v4.py`. Length kept at 73.8 s by choice; check.py now allows 40–76 s.

**v2 (63.6 s), A and C:** the package segment is now two lines. "Syrup AI Kit is open source, for native iOS and React
Native apps. It finds the tools your app should have, and writes the Swift that answers Siri." Then "Each tool stays
inside Siri's time limit, and failures turn into answers Siri can say. In Expo, one plugin sets up the whole build."
On screen: open-source/MIT pill, iOS and React Native chips, the siri-tools.json and generated Swift sheets, the 10 s
time budget with the three spoken replies, and the app.json plugin card. React Native support was confirmed by a
bare RN 0.88.1 build with the Swift package.

Vertical (1080×1920) cuts of the same script with Joanna's narration and burned-in captions, all passing `videos/siri-ai-ready/check.py` (size, codec, length, −16 LUFS, no blank frames). Design:
`docs/2026-11-14-siri-ai-ready-video-design.md`.

- `videos/siri-ai-ready/siri-ai-ready-a-hyperframes.mp4`: rendered in HyperFrames. The hook banner waves, the code
  sheets unfold like an accordion and the test results feed out of a printer slot, all drawn with HTML-in-Canvas.
- `videos/siri-ai-ready/siri-ai-ready-b-heygen.mp4`: version A's frames with a HeyGen presenter (Casey) speaking the
  "why" line full-frame and in picture-in-picture over the code and test scenes. 9 HeyGen premium credits. **Dropped
  (no presenter wanted); still the old 52 s v1 cut.**
- `videos/siri-ai-ready/siri-ai-ready-c-chrome.mp4`: the same scenes as one live page played in Chrome 157 and recorded
  through the DevTools screencast (`c-chrome/record.mjs`), so the effects are exactly as Chrome draws them.
- Opening shot: LTX-2.5 on Daytona, seed 7 (`shared/opening/opening.mp4`), from a still of generic app icons on a desk.
- Wikipedia appears only as an example built on its open-source app; the end card carries the Apple and Wikimedia
  non-affiliation lines.
- Example clip (40.3–58.9 s in v2): a real iPhone (`footage/answer-links/siri-phone-clip-tight.mp4`). The screen is QuickTime
  capture take 2. The sound is a separate Mac-mic take of Joanna's question and Siri's spoken answer, synced to the
  answer card. Siri's thinking time is trimmed to ~2 s. QuickTime's iPhone audio never records Siri's voice.
