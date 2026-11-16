# "Get your apps ready for Siri AI" launch video

A 74 s vertical (1080×1920) video for Syrup AI Kit, built with [HyperFrames](https://hyperframes.heygen.com) (HTML rendered to video).

## Layout

- `a-hyperframes/`: the HyperFrames project. `index.html` mounts one scene per file in `compositions/`.
  - `hook.html` is the opening waveform.
  - `syrup.html` is the WebGL syrup background. It starts pouring on the first spoken "Syrup".
- `shared/retime_v4.py`: builds the timing from the narration lines in `shared/narration/`. It writes:
  - `timeline.json` and `captions.json`
  - the captions scene
  - the root `index.html`
  - the syrup start time
  - `soundtrack.wav`, which mixes the narration with the clip audio taken from `shared/before-v2/soundtrack.wav`
- `check.py`: checks a finished render (size, codecs, length, loudness, blank frames). `test_check.py` holds its tests.
- `docs/`: the design, the plan and the shot list.

## Rebuild

```bash
python3 shared/retime_v4.py
cd a-hyperframes && npx --yes hyperframes@0.8.216 check
npx --yes hyperframes@0.8.216 render -o ../siri-ai-ready.mp4
cd .. && python3 check.py siri-ai-ready.mp4 --not-blank 2,10,20,40,70
```

`retime_v4.py` writes `shared/soundtrack.wav`. `a-hyperframes/assets/soundtrack.wav` is a copy of that file. In the original project the two were hard-linked, so copy the new soundtrack into `assets/` after a retime.
