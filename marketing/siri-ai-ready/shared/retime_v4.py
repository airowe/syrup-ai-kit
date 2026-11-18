"""Version 4: the locked "Siri hasn't been much help" script.

Lines: hook, why, package, discover, setup, wiki, then the phone clip, then close.
Writes timeline.json, captions.json, the captions scene, a-hyperframes/index.html and soundtrack.wav.
Everything is built from the line files in shared/narration/ and the version-1 soundtrack (for the clip's audio),
so it can be rerun.

    python3 shared/retime_v4.py
"""
import json
import re
import subprocess
from pathlib import Path

SHARED = Path(__file__).parent
VIDEO = SHARED.parent
A = VIDEO / "a-hyperframes"
V1_SOUNDTRACK = SHARED / "before-v2" / "soundtrack.wav"

HOOK_START = 0.4
GAP = 0.25
HOOK_GAP = 0.85  # room after the hook line to dismiss the Siri waveform
POUR_GAP = 0.75  # room before "Syrup AI Kit makes…" for the syrup pour into the package scene
SCENE_LEAD = 0.098
CLIP_AFTER_WIKI = 0.1
CLIP_SECONDS = 18.65
V1_CLIP_START = 28.667
CLOSE_OVERLAP = 0.5   # the close's syrup wipe starts this long before the clip ends
CLOSE_VOICE_AFTER_CLIP = 0.35
CLOSE_HOLD = 2.4      # end card held after the last word, for the small print
CLIP_CAPTIONS = [(1.0, 1.73, "In Wikipedia, how tall"), (2.73, 1.27, "is the Eiffel Tower?")]
LINES = ["hook", "why", "package", "discover", "setup", "wiki"]
MAX_WORDS = 5


def narration(name):
    data = json.loads((SHARED / "narration" / f"{name}.json").read_text())
    return data["words"], float(data["duration"]), data.get("text", "")


def chunk_captions(words, line_start):
    captions = []
    for i in range(0, len(words), MAX_WORDS):
        group = words[i:i + MAX_WORDS]
        following = words[i + MAX_WORDS] if i + MAX_WORDS < len(words) else None
        end = line_start + (following["start"] if following else group[-1]["end"])
        captions.append({"start_s": round(line_start + group[0]["start"], 3), "end_s": round(end, 3),
                         "text": " ".join(w["word"] for w in group)})
    return captions


def layout():
    starts, cursor = {}, HOOK_START
    for name in LINES:
        if name == "why":
            cursor += HOOK_GAP - GAP
        if name == "package":
            cursor += POUR_GAP - GAP
        starts[name] = round(cursor, 3)
        cursor += narration(name)[1] + GAP
    ends = {n: round(starts[n] + narration(n)[1], 3) for n in LINES}
    clip = round(ends["wiki"] + CLIP_AFTER_WIKI, 3)
    clip_end = round(clip + CLIP_SECONDS, 3)
    starts["close"] = round(clip_end + CLOSE_VOICE_AFTER_CLIP, 3)
    ends["close"] = round(starts["close"] + narration("close")[1], 3)
    length = round(ends["close"] + CLOSE_HOLD, 3)
    scene = lambda name: round(starts[name] - SCENE_LEAD, 3)
    package_scene = round(ends["why"] + 0.05, 3)
    scenes = {
        "hook": (0, scene("why")),
        "why": (scene("why"), round(starts["package"] - SCENE_LEAD, 3)),
        "package": (package_scene, scene("discover")),
        "discover": (scene("discover"), scene("setup")),
        "setup": (scene("setup"), scene("wiki")),
        "wikiintro": (scene("wiki"), clip),
        "close": (round(clip_end - CLOSE_OVERLAP, 3), length),
    }
    return starts, ends, clip, length, scenes


def main():
    starts, ends, clip, length, scenes = layout()
    timeline = []
    for name in LINES[:-1] + ["wiki"]:
        timeline.append({"id": name, "start_s": starts[name], "end_s": ends[name], "file": f"narration/{name}.mp3",
                         "text": narration(name)[2]})
    timeline.append({"id": "clip", "start_s": clip, "end_s": round(clip + CLIP_SECONDS, 3),
                     "file": "../../../footage/answer-links/siri-phone-clip-tight.mp4"})
    timeline.append({"id": "close", "start_s": starts["close"], "end_s": ends["close"], "file": "narration/close.mp3",
                     "text": narration("close")[2]})
    (SHARED / "timeline.json").write_text(json.dumps(timeline, indent=1))

    captions = []
    for name in LINES + ["close"]:
        captions += chunk_captions(narration(name)[0], starts[name])
    (SHARED / "captions.json").write_text(json.dumps(captions, indent=1))
    clip_captions = [(round(clip + offset, 3), duration, text) for offset, duration, text in CLIP_CAPTIONS]
    write_caption_scene(captions, clip_captions, length)
    write_root(scenes, clip, length)
    write_pour_start(starts, scenes)
    build_soundtrack(starts, clip, length)
    print(json.dumps({"starts": starts, "clip": clip, "length": length, "scenes": scenes}, indent=1))


def write_caption_scene(captions, clip_captions, length):
    path = A / "compositions/captions.html"
    text = path.read_text()
    rows = sorted([(c["start_s"], round(c["end_s"] - c["start_s"], 3), c["text"]) for c in captions] + clip_captions)
    divs = "\n".join(f'    <div id="cap-{i}" class="cap clip" data-start="{s}" data-duration="{d}"><span>{t}</span></div>'
                     for i, (s, d, t) in enumerate(rows))
    tweens = "\n".join(f'    tl.fromTo("#cap-{i} span", {{ y: 14, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.12, ease: "power2.out" }}, {s});'
                       for i, (s, _, _) in enumerate(rows))
    head = text[:text.index('    <div id="cap-0"')]
    script_head = '  </div>\n  <script>\n    const tl = gsap.timeline({ paused: true });\n'
    tail = f'    tl.to({{}}, {{ duration: {length} }}, 0);\n    window.__timelines["captions"] = tl;\n  </script>\n</template>\n'
    path.write_text(head + divs + "\n" + script_head + tweens + "\n" + tail)


def host(name, start, end, z=2):
    return (f'      <div id="{name}" class="scene clip" data-composition-id="{name}" data-composition-src="compositions/{name}.html" '
            f'data-start="{start:g}" data-duration="{round(end - start, 3):g}" data-track-index="1" data-track-kind="graphics" '
            f'style="z-index:{z}"></div>')


def write_root(scenes, clip, length):
    path = A / "index.html"
    text = path.read_text()
    body = "\n".join([
        f'    <div id="root" data-composition-id="main" data-start="0" data-duration="{length:g}" data-width="1080" data-height="1920">',
        host("hook", *scenes["hook"]),
        host("syrup", scenes["why"][0], length, z=1),
        host("why", *scenes["why"]),
        host("package", *scenes["package"], z=3),
        host("discover", *scenes["discover"]),
        host("setup", *scenes["setup"]),
        host("wikiintro", *scenes["wikiintro"]),
        f'      <video id="wiki-clip" class="clip" data-start="{clip:g}" data-duration="{CLIP_SECONDS:g}" data-track-index="0" src="assets/wiki-clip.mp4" muted playsinline></video>',
        host("close", *scenes["close"], z=3),
        f'      <div id="captions" class="scene clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{length:g}" data-track-index="2" data-track-kind="captions" style="z-index:5"></div>',
        f'      <audio id="soundtrack" class="clip" data-start="0" data-duration="{length:g}" data-track-index="3" src="assets/soundtrack.wav"></audio>',
        "    </div>",
    ])
    text = re.sub(r'    <div id="root".*?\n    </div>(?=\n    <script>)', lambda _: body, text, count=1, flags=re.S)
    text = re.sub(r"tl\.to\(\{\}, \{ duration: [\d.]+ \}\);", f"tl.to({{}}, {{ duration: {length:g} }});", text)
    path.write_text(text)


def write_pour_start(starts, scenes):
    """The syrup starts pouring on the first "Syrup" of the package line."""
    word = next(w for w in narration("package")[0] if "syrup" in w["word"].lower())
    pour_at = round(starts["package"] + word["start"] - scenes["why"][0], 3)
    path = A / "compositions/syrup.html"
    text = re.sub(r"const POUR_AT = [\d.]+;", f"const POUR_AT = {pour_at};", path.read_text())
    path.write_text(text)


def build_soundtrack(starts, clip, length):
    level = loudness(V1_SOUNDTRACK, 11.898, 8.15)
    names = LINES + ["close"]
    inputs = ["-i", str(V1_SOUNDTRACK)]
    chains = []
    for i, name in enumerate(names, start=1):
        ms = int(round(starts[name] * 1000))
        inputs += ["-i", str(SHARED / "narration" / f"{name}.mp3")]
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I={level}:TP=-1.5:LRA=11,"
                      f"aresample=48000,asetpts=N/SR/TB,adelay={ms}|{ms}[n{i}]")
    clip_ms = int(round(clip * 1000))
    chains.append(f"[0:a]atrim={V1_CLIP_START}:{V1_CLIP_START + CLIP_SECONDS},asetpts=N/SR/TB,"
                  f"adelay={clip_ms}|{clip_ms}[clip]")
    # adelay offsets timestamps rather than writing silence, and amix starts at the earliest input,
    # so a silent bed from 0 s keeps every line at its real time.
    chains.append(f"anullsrc=r=48000:cl=stereo,atrim=end={length}[bed]")
    mix = "[bed]" + "".join(f"[n{i}]" for i in range(1, len(names) + 1)) + "[clip]"
    chains.append(f"{mix}amix=inputs={len(names) + 2}:normalize=0:duration=longest,apad=pad_dur=5,atrim=end={length}[a]")
    # ffmpeg truncates in place, so the hard link a-hyperframes/assets/soundtrack.wav keeps pointing at this file.
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chains),
                    "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", str(SHARED / "soundtrack.wav")], check=True)


def loudness(path, start, seconds):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(start), "-t", str(seconds), "-i", str(path),
                          "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


if __name__ == "__main__":
    main()
