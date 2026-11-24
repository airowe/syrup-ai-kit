# Bluesky demo: review (second cut, "one conversation", 40.6 s)

Source: one continuous iPhone screen recording with system audio (`ScreenRecording_11-24-2026 15-54-47_1.MP4`). No "before" shot; the film opens on the first ask.

## Shots

| Film | Scene | Siri's real voice |
|---|---|---|
| 0–8.8 s | Ask 1 and the follower card; the number pops as Siri says it | "The Bluesky account @bsky.app has 35,827,450 followers." |
| 8.8–17.6 s | Ask 2 and the accounts card | "I found three Bluesky accounts for astronomy. Astronomy pictures, at astronomers.bsky.social". It cuts before Siri reads out "a telescope emoji". |
| 17.6–23.8 s | Ask 3, the confirmation, then "You tap Yes" with a click | "From Bluesky, are you sure you would like to continue?" |
| 23.8–34 s | "Bluesky opens the profile", the card, and the profile header | "From Bluesky, opening Astronomy pictures' profile." |
| 34–40.6 s | End card (unchanged) | Music fade-out |

## Passes

- `hyperframes check` passes. The warnings are expected:
  - nested media start times are local to each scene;
  - the small print sits under the length a closing line should get, the same as the launch video.
- **Sound:** an estimated −16.6 LUFS integrated, with peaks at −0.8 dBFS. The music sits about 9 dB lower under Siri's voice. It was mixed before render, so re-measure on the rendered file.
- **Privacy:** the cards are cropped to their opaque area. The profile shot is only the public header of @astronomers.bsky.social. Cut out:
  - your sidebar and avatar;
  - the loading frames;
  - the profile's posts;
  - Control Center (73.5 s and later).

## Known compromises

- **The three asks are my guesses.** Your voice wasn't recorded, so the asks are captions, and each is an editable variable (`ask1`, `ask2`, `ask3`):
  - "How many followers does bsky.app have on Bluesky?"
  - "Find Bluesky accounts about astronomy."
  - "Open the first one."
- A faint ghost of your handle shows through the glass under the accounts card.
- "You tap Yes" is placed where the confirmation card closes in the recording (54.5 s).

## Render

- `bluesky-demo.mp4`: 1080×1920, 40.6 s, H.264/AAC, −16.4 LUFS, peaks at −1.5 dBFS (measured on the file).
