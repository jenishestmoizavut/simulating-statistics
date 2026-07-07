#!/usr/bin/env python3
"""
Adds a 320x50 Adsterra Banner ad to every page of the site, pinned as a
sticky strip at the bottom of the viewport (same position on every page,
regardless of that page's own layout).

USAGE:
1. Clone your repo (if you haven't already):
   git clone https://github.com/jenishestmoizavut/simulating-statistics.git
   cd simulating-statistics

2. In Adsterra: Websites -> jenishestmoizavut.github.io -> Add Ad Unit
   -> Banner -> pick 320x50 -> Get Code. Copy the WHOLE snippet Adsterra
   gives you (it will include a <script> tag and usually a
   <div id="container-xxxxxxxx"></div>).

3. Paste that snippet into AD_SNIPPET below, replacing the placeholder.

4. Put this script in the repo root and run:
   python add_adsterra_banner.py

5. Check with `git diff`, open a couple of pages locally to eyeball it,
   then:
   git add -A
   git commit -m "Add Adsterra 320x50 banner to all pages"
   git push
"""

import os

ROOT_DIR = "."

# Paste the FULL snippet Adsterra gives you for the 320x50 Banner unit here.
AD_SNIPPET = """
<script>
  atOptions = {
    'key' : '00244a2b0b21b7020f7519a5319093fa',
    'format' : 'iframe',
    'height' : 50,
    'width' : 320,
    'params' : {}
  };
</script>
<script src="https://www.highperformanceformat.com/00244a2b0b21b7020f7519a5319093fa/invoke.js"></script>
"""

MARKER = "ADSTERRA-BANNER-INJECTED"
SKIP_DIRS = {".git", "node_modules", ".github", "_site"}

# The wrapper pins the banner to the bottom of the screen, centered,
# above everything else, with a small backdrop so it doesn't look broken
# on pages with light or dark backgrounds.
WRAPPER_TEMPLATE = """<!-- {marker} -->
<div style="position:fixed;left:0;right:0;bottom:0;z-index:9999;
display:flex;justify-content:center;align-items:center;
width:320px;height:50px;margin:0 auto;background:rgba(0,0,0,0.85);">
{snippet}
</div>
<!-- END {marker} -->
</body>"""


def find_html_files(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith((".html", ".htm")):
                found.append(os.path.join(dirpath, name))
    return found


def inject(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if MARKER in content:
        return "already-has-banner"
    if "</body>" not in content:
        return "no-body-tag"

    wrapper = WRAPPER_TEMPLATE.format(marker=MARKER, snippet=AD_SNIPPET)
    new_content = content.replace("</body>", wrapper, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return "updated"


def main():
    if "PASTE YOUR REAL ADSTERRA" in AD_SNIPPET:
        print("!! You haven't pasted your real Adsterra banner snippet into "
              "AD_SNIPPET yet. Edit this script first, then re-run.")
        return

    all_html = find_html_files(ROOT_DIR)
    if not all_html:
        print("No .html files found under", os.path.abspath(ROOT_DIR))
        return

    print(f"Found {len(all_html)} .html file(s). Injecting banner...\n")
    updated, skipped_existing, skipped_no_body = 0, 0, 0
    for path in all_html:
        result = inject(path)
        if result == "updated":
            print(f"updated:  {path}")
            updated += 1
        elif result == "already-has-banner":
            print(f"skip (already has it): {path}")
            skipped_existing += 1
        elif result == "no-body-tag":
            print(f"skip (no </body> found): {path}")
            skipped_no_body += 1

    print(f"\nDone. {updated} updated, {skipped_existing} already had it, "
          f"{skipped_no_body} skipped (no </body> tag).")


if __name__ == "__main__":
    main()