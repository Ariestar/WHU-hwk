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
    width: 960px;
  }}
  .window {{
    background-color: #161b22;
    border-radius: 10px;
    border: 1px solid #30363d;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.7);
    overflow: hidden;
    width: 100%;
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
    padding: 20px 22px;
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
    margin-bottom: 14px;
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

    # Estimate height based on line count
    total_lines = sum(len(out.splitlines()) + 3 for _, _, out in sessions)
    calc_height = max(300, min(total_lines * 24 + 140, 3200))
    calc_width = 1008

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

    # Crop with Pillow to content bounds + tight clean border
    im = Image.open(raw_png)
    # The body background is (11, 15, 20)
    # Crop to the actual terminal window
    w, h = im.size
    # Scan from bottom to find where window ends
    # Background color is (11, 15, 20)
    bg_color = im.getpixel((10, h - 5))
    bottom_cut = h
    for y in range(h - 1, 0, -2):
        row_diff = False
        for x in range(30, w - 30, 20):
            p = im.getpixel((x, y))
            if abs(p[0] - bg_color[0]) > 10 or abs(p[1] - bg_color[1]) > 10 or abs(p[2] - bg_color[2]) > 10:
                row_diff = True
                break
        if row_diff:
            bottom_cut = min(h, y + 28)
            break

    cropped = im.crop((0, 0, w, bottom_cut))
    cropped.save(output_png, optimize=True)

    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    if os.path.exists(raw_png):
        os.remove(raw_png)

    print(f"[+] 截图生成成功: {output_png} (尺寸: {cropped.size}, 大小: {os.path.getsize(output_png)} 字节)")

if __name__ == "__main__":
    print("Screenshot renderer module loaded.")
