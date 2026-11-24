# Bluesky demo: spec (storyline A, "Three asks, one app")

**The one thing:** Siri can use a real app's tools, built with Syrup AI Kit. It reads live data, searches, and asks before it writes anything.

**The viewer:** an iOS or Expo developer scrolling X or LinkedIn with the sound off.

## Format

- 1080×1920, 30 fps, H.264 and AAC, about 31 s.
- Silent footage. Each spoken request and each label is on-screen text. There is no voiceover.
- Every word sits between 168 px and 1330 px from the top. Keep the band below that free of text.

## Look (from the launch video)

- **Colours:** ground `#1b1712`, paper `#f4ead8`, syrup `#e0892c` (the accent; one use per beat), muted `#c9b89c`.
- **Type:** Outfit 700 for the asks (62 px), Inter 600 for labels (34 px, uppercase, tracked 0.08em), JetBrains Mono on the end card.
- **Phone footage:** the real Siri cards, cropped to the card and clipped to its rounded shape. A 1 px paper hairline marks the card's edge.

## Shots

| Time (s) | Beat | On screen |
|---|---|---|
| 0.0–6.2 | Ask 1 | The ask "In Bluesky, look up the profile bsky.app and tell me how many followers it has." is on screen from frame 0. The followers card rises in at 0.3 s. At 2.6 s, "35,769,650" lands in syrup, labelled "Live from Bluesky's API". |
| 6.2–12.4 | Ask 2 | "In Bluesky, find accounts about astronomy." The accounts card rises in. Label: "Real accounts, real handles". |
| 12.4–18.4 | Ask 3 | "Post 'hello from Siri' on Bluesky." The confirmation card rises in. Label: "Write actions ask first". At 16.4 s a paper chip reading “Yes” pops in. |
| 18.4–26.6 | Payoff | Label: "The composer opens. You tap Post." Below it, the real composer clip, scaled to 0.72. |
| 26.6–31.4 | End card | The launch end card, carried in: "Syrup AI Kit", the repo, the plugin, the Expo install command, and the small print, including "Bluesky example built on Bluesky's open-source app. Not affiliated with Bluesky Social, PBC." |

Within a beat, an ask holds its place once it lands. It doesn't drift or loop. Each ask enters a different way:

1. Ask 1 is already on screen at frame 0.
2. Ask 2 wipes in from the left.
3. Ask 3 types in word by word.

## Sound

- A HeyGen catalogue music bed: calm, warm, minimal tech, at about -16 LUFS. It fades in over 0.3 s and out over 1.5 s.
- A `pop` as each card lands, a `click-soft` on the "Yes" chip, and a `chime` when the composer appears.

## Banned

- Glow or particles. Things floating in a dark void.
- Every element fading and sliding up the same way.
- Text that keeps moving after it lands.
- A logo docked in a corner.
- Any frame showing the home screen, Gmail, notifications, the feed under a card, the volume indicator, or the evaluation's "Tool calls" bar.
- Apple logos or a mocked-up iPhone.
