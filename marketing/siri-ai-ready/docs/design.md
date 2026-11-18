# "Get your apps ready for Siri AI": social video, three ways

## Why

Apple opened the Siri AI Developer Preview to every developer on Nov 3, 2026, and says App Store submission opens in
the spring. Developers have a deadline. The video's job is to make iOS and Expo developers try Syrup AI Kit
(`expo-syrup-ai-kit` and the Swift package) to get their app ready, by showing that it's easy and that it works.

## Goals, non-goals, anti-goals

- **Goal:** one ~45 s vertical video for X and LinkedIn. It goes over the package, shows how it makes adapting an app
  for Siri AI easy, then uses Wikipedia as the example of what can be done.
- **Goal:** make it three ways (A, B, C below) from the same script and footage, so they can be compared and the best
  one posted.
- **Non-goal:** a series of shorts, a long walkthrough, or a landscape cut. One video only.
- **Anti-goal:** implying we changed Wikipedia's app, or that Wikimedia endorses this. Wikipedia is an example of what
  can be done, built on its open-source app.
- **Anti-goal:** anything that reads as Apple's: no Apple logos, no imitation of Apple's typefaces or Siri's look on our
  own cards, no generated iPhones. The iPhone footage is real.
- **Anti-goal:** claims we haven't measured. Numbers on screen come from `syrup-ai-eval summarize` runs.

## Constraints

- 1080×1920, H.264 + AAC, about 45 s (40–52 s is fine).
- Captions burned in: feeds autoplay muted.
- Voice: HeyGen "Joanna – Warm & Conversational" (voice id `776f9d2ff401499a8f1f2bcb4ca46004`, en-US), this project's
  voice in `.media/preferences.json`. No "Hey Siri" anywhere in the audio, so the video doesn't wake viewers' phones.
- Small print on the end card: "Not affiliated with or endorsed by Apple. Siri and iPhone are trademarks of Apple Inc.,
  registered in the U.S. and other countries and regions." and "Example built on Wikipedia's open-source iOS app. Not
  affiliated with the Wikimedia Foundation."
- No private footage: no home screen, notifications, personal notes or the evaluation's "Tool calls" bar.
- Deliverables go in the project folder; working files stay out of the footage folder.

## Script (shared by all three)

Narration by Joanna, ~110 words. Times are targets.

| Time | Narration | On screen |
|---|---|---|
| 0–4 s | "Get your apps ready for Siri AI." | Hook text over the LTX opening shot |
| 4–12 s | "Siri AI is in preview for every developer now, and App Store support comes in the spring. Siri can call your app's tools, if it has them." | "Developer preview: now. App Store: spring." |
| 12–22 s | "Syrup AI Kit wraps the API code you already have in a tool Siri can call. In Expo, it's a few lines of JSON." | The README's generic Swift example (`tool.answer { describe(try await MyAPI.shared.cart()) }`), then the README's `siri-tools.json` tool. Not Wikipedia's code |
| 22–28 s | "Then it tests your tool with Siri on a real iPhone, so you know it works." | The README's "Measured on a phone" results, labelled as the kit's sample tools: "A tool that reads a live API: 5 of 5", "An enum parameter: 5 of 5", "A write action that asks to confirm: 5 of 5". Not a claim about the Wikipedia clip |
| 28–47 s | "Here's what that looks like in an open-source app like Wikipedia." (spoken over the end of the previous scene) then the whole voiced clip plays (18.65 s, 1080×2008, centre-cropped to 1920 tall): the question, Siri's reply, the app opening at the highlighted answer | `footage/answer-links/eiffel-siri-opens-at-answer-voiced.mp4` |
| 47–52 s | "Syrup AI Kit. Get your app ready today." | End card: `npx expo install expo-syrup-ai-kit expo-app-intents` (the README's working command), the Swift package URL, `github.com/airowe/syrup-ai-kit`, the small print |

## The opening shot (all three)

One LTX-2.5 clip, made with a local LTX cutscene tool on Daytona GPUs (image to video: a still plus a prompt, 5 s).
Vertical, 896×1536, scaled to 1080×1920. Subject: generic app icons (our own shapes and colours, no Apple look) lifting
off a desk and lining up, leaving room at the top for the hook text. Several seeds; pick the best. The still is made
by us (a HyperFrames frame), not taken from Apple material.

## The three versions

- **A, HyperFrames.** An HTML composition rendered to video. HTML-in-Canvas effects on our own cards: the code
  snippets as sheets that fold into place, the results printing out, the hook banner waving in. The LTX shot and the
  Wikipedia clip play inside it. Captions from the narration's word timings. The renderer's Chrome (152) only has
  HTML-in-Canvas with `--enable-blink-features=CanvasDrawElement`; test that a render can turn it on first, and fall
  back to CSS 3D for the same scenes if it can't.
- **B, HeyGen presenter.** A HeyGen avatar video speaking the script in Joanna's voice, from the subscription's free
  allowance (Creator plan, 402 premium credits left on Nov 14, resetting Dec 1; check the cost estimate before submitting, and stop if one take would use more than a quarter of what's left). The LTX opening, code, results and Wikipedia clip are cut in as inserts (full-frame or picture-in-picture),
  with the same captions and end card.
- **C, live Chrome recording.** The same scenes as A, built as one live HTML-in-Canvas page that plays itself, opened in
  Chrome 157 (installed on the Mac) with a 1080×1920 viewport and recorded frame by frame through the DevTools protocol (no screen capture, no Retina doubling; I run it, the user doesn't), then cut together with the narration, LTX opening and
  Wikipedia clip with ffmpeg.

## Approaches considered

All three are being made, at the user's request. The user picked them over a single approach so the results can be
compared. The trade-offs: A gives frame-exact timing and cheap re-renders; B gives a human face but reads more like an
ad and costs HeyGen allowance; C shows the effects exactly as Chrome draws them but its timing comes from a recording.

## Calls I made (correct any)

- Narration wording and timings above.
- The opening shot's subject.
- B's presenter: a stock HeyGen avatar whose look suits Joanna's voice, chosen from the catalogue; the user picks if
  there are several close ones.
- Wikipedia's question in the clip is also spoken by Joanna, as recorded.
- Version files: `siri-ai-ready-a-hyperframes.mp4`, `-b-heygen.mp4`, `-c-chrome.mp4`.

## Settled after the builder check

- The on-screen results are the README's measured sample tools, labelled as such; the answer-link clip has no number
  on it (only 1 of its 6 runs completed in Apple's harness).
- The install command includes `expo-app-intents`, matching the README. The JSON scene shows only `siri-tools.json`.
- The Swift snippet is the README's generic example, so the package scene is about the package, and Wikipedia's code
  isn't shown as if we changed Wikimedia's app.
- C is recorded headlessly from Chrome 157 over the DevTools protocol at an exact 1080×1920 viewport.
- The Wikipedia clip plays whole; the video runs to about 52 s.

## Left to the builder

Fonts and colours (ours, not Apple's), the exact effects per scene, caption styling, the music bed if any (quiet,
licensed or generated), and the LTX prompt wording.
