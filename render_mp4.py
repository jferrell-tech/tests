"""
Renders SportsCarLoader animation to MP4 using Pillow + imageio-ffmpeg.
Produces one full lap (2.5 seconds) at 60 fps → 150 frames, 480x560px.
"""

import math
import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw

# --- constants ---
FPS = 60
DURATION = 2.5          # seconds per lap
TOTAL_FRAMES = int(FPS * DURATION)

W, H_ANIM = 480, 480    # SVG canvas size
PADDING = 40            # extra vertical space for heading + status
FULL_H = H_ANIM + 120   # heading above + status below

CX, CY = W // 2, H_ANIM // 2 + 60   # shifted down to leave room for heading
TRACK_R = 80 * (W / 240)             # scale radius with canvas

CAR_COLOR   = (249, 115, 22)         # #F97316
GREEN       = (34,  197, 94)         # #22c55e
ORANGE      = (249, 115, 22)
TRACK_BG    = (226, 232, 240)        # #e2e8f0
BG_COLOR    = (255, 255, 255)        # white background
TEXT_COLOR  = (0,   0,   0)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_circle_outline(draw, cx, cy, r, color, width=6):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


def draw_arc(draw, cx, cy, r, start_deg, end_deg, color, width=6):
    """Draw an arc from start_deg to end_deg (degrees, 0=3-o'clock, CCW in PIL)."""
    bbox = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(bbox, start=start_deg, end=end_deg, fill=color, width=width)


def draw_car(img, cx, cy, angle_rad, color):
    """
    Draw a side-view sports car centred at (cx, cy), rotated by angle_rad.
    We composite a small car image rotated to the right angle.
    """
    CAR_W, CAR_H = 90, 50
    car = Image.new("RGBA", (CAR_W + 80, CAR_H + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(car)

    ox, oy = 40, 20   # local origin

    # body
    d.rounded_rectangle([ox - 44, oy - 8, ox + 44, oy + 13], radius=8, fill=color + (255,))
    # cabin
    d.polygon([(ox - 16, oy - 8), (ox - 28, oy - 28), (ox + 16, oy - 28), (ox + 28, oy - 8)], fill=color + (255,))
    # windshield (dark)
    d.polygon([(ox - 12, oy - 9), (ox - 22, oy - 27), (ox + 12, oy - 27), (ox + 22, oy - 9)], fill=(30, 41, 59, 178))
    # front bumper
    d.rounded_rectangle([ox + 36, oy - 8, ox + 48, oy + 8], radius=4, fill=color + (255,))
    # rear bumper
    d.rounded_rectangle([ox - 48, oy - 8, ox - 36, oy + 8], radius=4, fill=color + (255,))
    # spoiler horizontal
    d.rectangle([ox - 44, oy - 24, ox - 28, oy - 20], fill=color + (255,))
    # spoiler vertical fin
    d.rectangle([ox - 40, oy - 32, ox - 16, oy - 24], fill=color + (255,))
    # front wheel
    d.ellipse([ox + 18, oy + 2, ox + 38, oy + 22], fill=(30, 41, 59, 255))
    d.ellipse([ox + 23, oy + 7, ox + 33, oy + 17], fill=(148, 163, 184, 255))
    # rear wheel
    d.ellipse([ox - 38, oy + 2, ox - 18, oy + 22], fill=(30, 41, 59, 255))
    d.ellipse([ox - 33, oy + 7, ox - 23, oy + 17], fill=(148, 163, 184, 255))
    # headlight
    d.rectangle([ox + 44, oy - 6, ox + 50, oy + 2], fill=(254, 240, 138, 255))
    # tail light
    d.rectangle([ox - 50, oy - 6, ox - 44, oy + 2], fill=(239, 68, 68, 255))
    # speed lines
    for dy, length, alpha in [(-4, 16, 130), (4, 12, 100), (-10, 8, 80)]:
        line_color = (148, 163, 184, alpha)
        d.line([(ox - 52, oy + dy), (ox - 52 - length, oy + dy)], fill=line_color, width=3)

    # rotate car to face tangent direction (angle + 90 deg)
    rotate_deg = math.degrees(angle_rad) + 90
    car = car.rotate(-rotate_deg, expand=True, resample=Image.BICUBIC)

    # paste onto main image
    paste_x = int(cx - car.width / 2)
    paste_y = int(cy - car.height / 2)
    img.paste(car, (paste_x, paste_y), car)


def draw_checkmark(draw, x, y, r=9):
    """Green filled circle with white checkmark."""
    draw.ellipse([x - r, y - r, x + r, y + r], fill=GREEN + (255,))
    pts = [(x - r * 0.5, y), (x - r * 0.1, y + r * 0.45), (x + r * 0.6, y - r * 0.5)]
    draw.line(pts, fill=(255, 255, 255, 255), width=2)


def draw_spinner(draw, x, y, r=9, progress=0):
    """Small orange arc spinner that rotates based on progress."""
    bbox = [x - r, y - r, x + r, y + r]
    # grey track
    draw.ellipse(bbox, outline=(203, 213, 225, 255), width=3)
    # orange arc (90 degrees)
    start = -90 + progress * 360
    draw.arc(bbox, start=start, end=start + 90, fill=ORANGE + (255,), width=3)


def draw_status_items(draw, base_x, base_y, spinner_progress):
    items = [
        ("check", "Drivers added"),
        ("check", "Vehicles added"),
        ("spinner", "Calculating your rate"),
    ]
    for i, (icon, label) in enumerate(items):
        iy = base_y + i * 28
        if icon == "check":
            draw_checkmark(draw, base_x, iy)
        else:
            draw_spinner(draw, base_x, iy, progress=spinner_progress)
        draw.text((base_x + 18, iy - 9), label, fill=TEXT_COLOR + (255,), font_size=18)


# ---------------------------------------------------------------------------
# Frame renderer
# ---------------------------------------------------------------------------

def render_frame(frame_idx):
    progress = (frame_idx / TOTAL_FRAMES)
    angle = progress * 2 * math.pi - math.pi / 2  # start at top

    img = Image.new("RGBA", (W, FULL_H), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # --- heading ---
    draw.text((W // 2, 28), "Preparing Your Quote", fill=TEXT_COLOR + (255,),
              font_size=26, anchor="mm")

    # --- track background ---
    draw_circle_outline(draw, CX, CY, TRACK_R, TRACK_BG + (255,), width=8)

    # --- orange trail arc ---
    if progress > 0:
        trail_end_deg   = -90 + progress * 360   # PIL: 0=3-o'clock
        trail_start_deg = -90
        alpha = int(0.45 * 255)
        draw_arc(draw, CX, CY, TRACK_R,
                 start_deg=trail_start_deg,
                 end_deg=trail_end_deg,
                 color=CAR_COLOR + (alpha,),
                 width=8)

    # --- car ---
    car_x = CX + TRACK_R * math.cos(angle)
    car_y = CY + TRACK_R * math.sin(angle)
    draw_car(img, car_x, car_y, angle, CAR_COLOR)

    # --- status items ---
    status_y_start = H_ANIM + 72
    status_x = W // 2 - 90
    draw_status_items(draw, status_x, status_y_start, spinner_progress=progress)

    return np.array(img.convert("RGB"))


# ---------------------------------------------------------------------------
# Encode to MP4
# ---------------------------------------------------------------------------

frames = [render_frame(i) for i in range(TOTAL_FRAMES)]

out_path = "/home/user/tests/SportsCarLoader.mp4"
iio.imwrite(
    out_path,
    frames,
    fps=FPS,
    codec="libx264",
    quality=8,
    pixelformat="yuv420p",
)

print(f"Wrote {len(frames)} frames → {out_path}")
