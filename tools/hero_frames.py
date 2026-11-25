"""A capture's frame sequence -> the live part's looping video for a 3D hero (hero3d.js plays it on the part's emissive texture).

  python hero_frames.py <frames dir> <out base> [--mask layer.png] [--crop x0,y0,x1,y1] [--fps 25] [--width 1024]

--mask: a capture layer whose alpha cuts the part out of each frame (the Limiter's L_vfd.png: the VFD window alone), so the video
        holds exactly what the still's layer held; --crop: the part's box in frame pixels (default: the mask's bounding box,
        padded 8 px and rounded to even). Writes <out base>.webm (VP9) and <out base>.mp4 (H.264, Safari), the first frame as
        <out base>.png (the GLB's poster texture), and <out base>.crop.json ({"crop": [x0, y0, x1, y1], "size": [W, H]}): hero_glb.py
        LIVE_CROP=<that json> maps the part's UVs onto the cropped video."""
import argparse, json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("frames"); ap.add_argument("out")
ap.add_argument("--mask"); ap.add_argument("--crop"); ap.add_argument("--fps", type=float, default=25); ap.add_argument("--width", type=int, default=1024)
a = ap.parse_args()
fs = sorted(f for f in os.listdir(a.frames) if f.lower().endswith(".png"))
if not fs: sys.exit("no frames in " + a.frames)
W, H = Image.open(os.path.join(a.frames, fs[0])).size
mask = None
if a.mask:
    m = Image.open(a.mask).convert("RGBA")
    if m.size != (W, H): sys.exit(f"mask {m.size} != frames {(W, H)}")
    mask = np.asarray(m)[..., 3:4].astype(np.float32) / 255
if a.crop: x0, y0, x1, y1 = map(int, a.crop.split(","))
elif mask is not None:
    ys, xs = np.nonzero(mask[..., 0] > 0.02); x0, y0, x1, y1 = xs.min() - 8, ys.min() - 8, xs.max() + 9, ys.max() + 9
else: x0, y0, x1, y1 = 0, 0, W, H
x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W, x1), min(H, y1)
x1 -= (x1 - x0) % 2; y1 -= (y1 - y0) % 2
tmp = tempfile.mkdtemp(prefix="hero_frames_")
for i, f in enumerate(fs):
    im = np.asarray(Image.open(os.path.join(a.frames, f)).convert("RGB")).astype(np.float32)
    if mask is not None: im = im * mask
    Image.fromarray(im[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)).save(os.path.join(tmp, "c_%04d.png" % i))
    if i == 0: Image.fromarray(im[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)).save(a.out + ".png")
w = min(a.width, x1 - x0); w -= w % 2
vf = f"scale={w}:-2:flags=lanczos,format=yuv420p"
src = ["-framerate", str(a.fps), "-i", os.path.join(tmp, "c_%04d.png")]
subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-vf", vf, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", "-row-mt", "1", "-an", a.out + ".webm"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-vf", vf, "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-an", a.out + ".mp4"], check=True)
json.dump({"crop": [int(x0), int(y0), int(x1), int(y1)], "size": [W, H], "frames": len(fs), "fps": a.fps}, open(a.out + ".crop.json", "w"))
print("wrote", a.out + ".webm/.mp4", os.path.getsize(a.out + ".webm"), os.path.getsize(a.out + ".mp4"), "bytes; crop", (x0, y0, x1, y1))
