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
ap.add_argument("--xfade", type=int, default=0, help="blend the last N frames toward the first N, so the loop has no seam")
ap.add_argument("--agx", type=float, default=1.0, help="saturation boost against the viewer's AgX tone mapping (1 = off); match it to the still")
ap.add_argument("--tint", default="1,1,1", help="r,g,b gains before the --agx boost, to match the still's hue")
ap.add_argument("--gloss", help="angle,offset,soft,amount: a soft grey sheen added over the part (the still's glass reflection the model can't mirror)")
a = ap.parse_args()
# The viewer shows the video as emission through AgX, which pulls bright colours toward cream. --agx boosts the saturation ahead of
# it and pulls the darks down so the boost doesn't lift a dark background; pick the value whose model shot matches the still.
TINT = np.float32([float(v) for v in a.tint.split(",")])
def grade(im):
    lum = (im @ np.float32([0.2126, 0.7152, 0.0722]))[..., None] / 255
    im = im * (1 + (TINT - 1) * np.clip(lum * 3, 0, 1))   # tint the lit parts only, so a dark background keeps its own colour
    if a.agx != 1:
        y = im @ np.float32([0.2126, 0.7152, 0.0722])
        im = y[..., None] + (im - y[..., None]) * a.agx
        im = np.interp(im.clip(0, 255) / 255, [0, 0.2, 0.5, 1], [0, 0.06, 0.42, 1]).astype(np.float32) * 255
    if a.gloss:   # a reflection the still has and the model's environment can't give: a soft band of grey across the part
        ang, off, soft, amt = map(float, a.gloss.split(","))
        h, w = im.shape[:2]; v, u = np.mgrid[-1:1:h * 1j, -1:1:w * 1j]
        d = u * np.cos(np.radians(ang)) + v * np.sin(np.radians(ang)) - off
        t = np.clip((d + soft) / (2 * soft), 0, 1); im = im + (amt * t * t * (3 - 2 * t))[..., None]
    return im
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
load = lambda f: np.asarray(Image.open(os.path.join(a.frames, f)).convert("RGB")).astype(np.float32)
# --xfade N: the loop is cut N frames short and its first N frames fade in from the last N, so the end runs into the start
# (out[j] = mix(frame[n-N+j], frame[j]) for j < N; the video is n - N frames long)
n, N = len(fs), a.xfade
for i in range(n - N):
    im = load(fs[i])
    if i < N:
        t = (i + 1) / (N + 1); im = load(fs[n - N + i]) * (1 - t) + im * t
    if mask is not None: im = im * mask
    Image.fromarray(grade(im[y0:y1, x0:x1]).clip(0, 255).astype(np.uint8)).save(os.path.join(tmp, "c_%04d.png" % i))
    if i == N: Image.fromarray(im[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)).save(a.out + ".png")   # an unblended frame
w = min(a.width, x1 - x0); w -= w % 2
vf = f"scale={w}:-2:flags=lanczos,format=yuv420p"
src = ["-framerate", str(a.fps), "-i", os.path.join(tmp, "c_%04d.png")]
subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-vf", vf, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", "-row-mt", "1", "-an", a.out + ".webm"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-vf", vf, "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-an", a.out + ".mp4"], check=True)
json.dump({"crop": [int(x0), int(y0), int(x1), int(y1)], "size": [W, H], "frames": n - N, "fps": a.fps}, open(a.out + ".crop.json", "w"))
print("wrote", a.out + ".webm/.mp4", os.path.getsize(a.out + ".webm"), os.path.getsize(a.out + ".mp4"), "bytes; crop", (x0, y0, x1, y1))
