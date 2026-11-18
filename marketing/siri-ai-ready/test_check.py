import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
CHECK = HERE / "check.py"
SHARED = HERE / "shared"
WIDTH, HEIGHT = 1080, 1920
CAPTION_TOLERANCE_S = 0.15
SMALL_TITLE_BOX = (440, 80)  # about 2% of the frame, like a lone title on the dark background


def make_clip(path, width, height, seconds, colour="0x3366aa", noise=True, box=None):
    video = f"color=c={colour}:s={width}x{height}:d={seconds}"
    if box:
        video += f",drawbox=x=70:y=190:w={box[0]}:h={box[1]}:color=0xf4ead8:t=fill"
    if noise:
        video += ",noise=alls=60:allf=t"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", video,
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-shortest", str(path)],
        check=True,
    )


def run_check(*args):
    return subprocess.run([sys.executable, str(CHECK), *map(str, args)], capture_output=True, text=True)


class CheckTests(unittest.TestCase):
    def setUp(self):
        (HERE / ".test-output").mkdir(exist_ok=True)
        self.dir = tempfile.TemporaryDirectory(dir=HERE / ".test-output")
        self.tmp = Path(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_rejects_wrong_size(self):
        clip = self.tmp / "square.mp4"
        make_clip(clip, 1080, 1080, 2)
        result = run_check(clip)
        self.assertEqual(result.returncode, 1)
        self.assertIn("size", result.stdout)

    def test_rejects_blank_frame(self):
        clip = self.tmp / "flat.mp4"
        make_clip(clip, WIDTH, HEIGHT, 45, noise=False)
        result = run_check(clip, "--not-blank", "1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("blank", result.stdout)

    def test_accepts_dark_frame_with_little_text(self):
        clip = self.tmp / "sparse.mp4"
        make_clip(clip, WIDTH, HEIGHT, 45, colour="0x1b1712", noise=False, box=SMALL_TITLE_BOX)
        result = run_check(clip, "--not-blank", "1")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_accepts_good_file(self):
        clip = self.tmp / "good.mp4"
        make_clip(clip, WIDTH, HEIGHT, 45)
        result = run_check(clip, "--not-blank", "1,20")
        self.assertEqual(result.returncode, 0, result.stdout)


class CaptionTests(unittest.TestCase):
    def test_captions_match_words(self):
        timeline = json.loads((SHARED / "timeline.json").read_text())
        captions = json.loads((SHARED / "captions.json").read_text())
        starts = []
        for item in timeline:
            if item["id"] == "clip":
                continue
            words = json.loads((SHARED / "narration" / f"{item['id']}.json").read_text())["words"]
            starts += [item["start_s"] + word["start"] for word in words]
        for caption in captions:
            nearest = min(abs(caption["start_s"] - start) for start in starts)
            self.assertLessEqual(nearest, CAPTION_TOLERANCE_S, caption)
        self.assertTrue(all(len(c["text"].split()) <= 5 for c in captions))


if __name__ == "__main__":
    unittest.main()
