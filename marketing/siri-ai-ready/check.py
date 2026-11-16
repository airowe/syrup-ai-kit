"""Checks a finished video against the design: size, codecs, length, loudness and, optionally, non-blank frames.

    python3 check.py <video.mp4> [--not-blank 2,10,16]

Prints one line per failed check and exits 1 if any failed.
"""
import json
import re
import subprocess
import sys

WIDTH, HEIGHT = 1080, 1920
MIN_SECONDS, MAX_SECONDS = 40, 76
TARGET_LUFS, LUFS_TOLERANCE = -16, 1
# A frame whose brightness spans fewer levels than this is a flat card or an undrawn canvas.
MIN_LUMA_RANGE = 24


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
         "-of", "json", path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    found = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    return float(found[-1]) if found else None


def luma_range(path, seconds):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(seconds), "-i", path, "-frames:v", "1",
                          "-vf", "signalstats,metadata=print", "-f", "null", "-"], capture_output=True, text=True).stderr
    low = re.search(r"YMIN=([\d.]+)", err)
    high = re.search(r"YMAX=([\d.]+)", err)
    return float(high.group(1)) - float(low.group(1)) if low and high else 0.0


def problems(path, blank_times):
    info = probe(path)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    duration = float(info["format"]["duration"])
    found = []
    if not video or (video["width"], video["height"]) != (WIDTH, HEIGHT):
        found.append(f"size: {video and (video['width'], video['height'])}, want {WIDTH}x{HEIGHT}")
    if not video or video["codec_name"] != "h264":
        found.append(f"video codec: {video and video['codec_name']}, want h264")
    if not audio or audio["codec_name"] != "aac":
        found.append(f"audio codec: {audio and audio['codec_name']}, want aac")
    if not MIN_SECONDS <= duration <= MAX_SECONDS:
        found.append(f"length: {duration:.2f} s, want {MIN_SECONDS}-{MAX_SECONDS} s")
    level = loudness(path) if audio else None
    if level is None or abs(level - TARGET_LUFS) > LUFS_TOLERANCE:
        found.append(f"loudness: {level} LUFS, want {TARGET_LUFS} ±{LUFS_TOLERANCE}")
    for seconds in blank_times:
        spread = luma_range(path, seconds)
        if spread < MIN_LUMA_RANGE:
            found.append(f"blank frame at {seconds} s (brightness range {spread:.0f})")
    return found


def main(argv):
    path, blank_times = argv[0], []
    if "--not-blank" in argv:
        blank_times = [float(t) for t in argv[argv.index("--not-blank") + 1].split(",")]
    found = problems(path, blank_times)
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
