#!/usr/bin/env python3
import os
import subprocess
import html
from PIL import Image

SCREENSHOTS_DIR = "/home/wolllf/Coding/WHU-hwk/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    background-color: #0b0f14;
    font-family: 'Maple Mono NF CN', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
    display: inline-block;
    padding: 24px;
    width: 1040px;
  }}
  .window {{
    background-color: #161b22;
    border-radius: 10px;
    border: 1px solid #30363d;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.7);
    overflow: hidden;
    width: 100%;
    margin-bottom: 24px;
  }}
  .titlebar {{
    background-color: #21262d;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #30363d;
  }}
  .controls {{
    display: flex;
    gap: 8px;
    width: 60px;
  }}
  .dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
  }}
  .dot-red {{ background-color: #ff5f56; }}
  .dot-yellow {{ background-color: #ffbd2e; }}
  .dot-green {{ background-color: #27c93f; }}
  .title {{
    flex: 1;
    text-align: center;
    color: #8b949e;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
    padding-right: 60px;
  }}
  .terminal-body {{
    padding: 20px 24px;
    color: #e6edf3;
    font-size: 13.5px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-all;
  }}
  .prompt-line {{
    margin-bottom: 8px;
    display: block;
  }}
  .prompt-user {{ color: #58a6ff; font-weight: bold; }}
  .prompt-sep {{ color: #8b949e; }}
  .prompt-path {{ color: #7ee787; font-weight: bold; }}
  .prompt-symbol {{ color: #f0883e; font-weight: bold; }}
  .cmd-text {{ color: #ffa657; font-weight: bold; }}
  .cmd-output {{
    color: #c9d1d9;
    margin-bottom: 18px;
  }}
</style>
</head>
<body>
<div class="window" id="terminal-window">
  <div class="titlebar">
    <div class="controls">
      <span class="dot dot-red"></span>
      <span class="dot dot-yellow"></span>
      <span class="dot dot-green"></span>
    </div>
    <div class="title">{title}</div>
  </div>
  <div class="terminal-body">
{body_content}
  </div>
</div>
</body>
</html>
"""

def render_session(title, sessions, output_png):
    """
    sessions: list of tuples (path, command, output)
    Renders terminal session into high-resolution PNG with complete window bounds.
    """
    body_parts = []
    for path, cmd, out in sessions:
        escaped_cmd = html.escape(cmd)
        escaped_out = html.escape(out)
        part = f"""    <div class="prompt-line">
      <span class="prompt-user">wolllf@ubuntu</span><span class="prompt-sep">:</span><span class="prompt-path">{path}</span><span class="prompt-symbol">$</span> <span class="cmd-text">{escaped_cmd}</span>
    </div>
    <div class="cmd-output">{escaped_out}</div>"""
        body_parts.append(part)

    full_html = HTML_TEMPLATE.format(
        title=html.escape(title),
        body_content="\n".join(body_parts)
    )

    tmp_html = f"/tmp/screenshot_{os.path.basename(output_png)}.html"
    raw_png = f"/tmp/raw_{os.path.basename(output_png)}"

    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Use a tall viewport (8000px) so Chrome never truncates any content
    calc_width = 1120
    calc_height = 8000

    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={calc_width},{calc_height}",
        f"--screenshot={raw_png}",
        tmp_html
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Automatically detect true element bounds using Pillow
    im = Image.open(raw_png)
    w, h = im.size
    bg = im.getpixel((0, 0))

    # Scan from bottom upwards to find true end of content & shadow
    bottom_y = 0
    for y in range(h - 1, 0, -2):
        has_content = False
        for x in range(30, w - 30, 15):
            p = im.getpixel((x, y))
            if any(abs(p[i] - bg[i]) > 8 for i in range(3)):
                has_content = True
                break
        if has_content:
            bottom_y = y
            break

    # Scan left and right bounds
    min_x, max_x = w, 0
    min_y = 0
    for y in range(bottom_y + 1):
        for x in range(10, w - 10, 5):
            p = im.getpixel((x, y))
            if any(abs(p[i] - bg[i]) > 8 for i in range(3)):
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if min_y == 0 and y > 0: min_y = y

    pad = 20
    crop_box = (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + pad),
        min(h, bottom_y + pad)
    )

    cropped = im.crop(crop_box)
    cropped.save(output_png, optimize=True)

    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    if os.path.exists(raw_png):
        os.remove(raw_png)

    print(f"[+] 截图生成成功: {output_png} (尺寸: {cropped.size}, 大小: {os.path.getsize(output_png)} 字节)")

if __name__ == "__main__":
    print("Screenshot renderer module loaded.")
