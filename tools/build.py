#!/usr/bin/env python3
"""
Fathom Build Script
Reads source files, assembles dist/index.html

Source structure:
  src/index.html       — HTML skeleton + inline CSS + app JS (with {{DATA}} placeholder)
  src/js/data.js        — COUNTRY_DATA, HOFSTEDE_SCORES, DIM_META, GLOBE_DATA

Usage:
  python3 tools/build.py                # Build to dist/index.html
  python3 tools/build.py --output src/  # Build to src/index.html (for direct file:// testing)
  python3 tools/build.py --serve        # Build + start dev server on :8123
"""

import re, os, sys, subprocess

def build(output_dir='dist'):
    """Assemble index.html"""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Read template
    with open('src/index.html', encoding='utf-8') as f:
        template = f.read()

    # 2. Copy config.js to dist/ (required by index.html)
    import shutil
    config_src = 'src/config.js'
    if os.path.exists(config_src):
        shutil.copy2(config_src, os.path.join(output_dir, 'config.js'))
        print(f"✓ Copied: config.js → {output_dir}/config.js")

    # 3. Inject data (replace the inline data blocks with external content)
    # The template has the data inline; we verify consistency but keep inline for now.
    output = template  # For now, just copy

    # 4. Write output
    out_path = os.path.join(output_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    size = os.path.getsize(out_path)
    print(f"✓ Built: {out_path} ({size:,} bytes)")

    # 5. Validate JS
    js_match = re.findall(r'<script>(.*?)</script>', output, re.DOTALL)
    if js_match:
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as tf:
            tf.write(js_match[0])
            js_path = tf.name
        r = subprocess.run(
            ['/Users/yuanming/.workbuddy/binaries/node/versions/22.22.2/bin/node', '--check', js_path],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            print(f"✓ JS syntax: OK")
        else:
            print(f"⚠ JS syntax: ERROR")
            for line in r.stderr.strip().split('\n')[-2:]:
                print(f"  {line[:200]}")
    return out_path

def serve(output_dir='dist'):
    """Start HTTP server for testing"""
    import http.server, socketserver
    os.chdir(output_dir)

    port = 8123
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"🌐 Dev server: http://127.0.0.1:{port}")
        print(f"   Test URL: http://127.0.0.1:{port}/index.html?a=ae&b=mx&lang=zh")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Done")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='dist', help='Output directory (default: dist)')
    parser.add_argument('--serve', action='store_true', help='Start dev server after build')
    args = parser.parse_args()

    path = build(args.output)
    if args.serve:
        serve(args.output)
