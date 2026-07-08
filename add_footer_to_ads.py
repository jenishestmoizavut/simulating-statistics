#!/usr/bin/env python3
"""
Adds/updates a small disclaimer footer to every page of the site, noting
that ads are served by AdSterra, are not personally endorsed, and that
you (the site owner) should not be held liable for their content.

USAGE:
1. cd into your repo (root, not simulations/):
   cd simulating-statistics

2. Adjust DISCLAIMER_TEXT / styling below if you want to tweak it.

3. Run:
   python add_footer_to_ads.py

4. Check with `git diff --stat`, eyeball a page or two locally, then:
   git add -A
   git commit -m "Restyle AdSterra disclaimer footer + fix disclaimer link"
   git push
"""

import os
import re

ROOT_DIR = "."

DISCLAIMER_TEXT = (
    'Ads on this site are served by AdSterra and are not personally endorsed by the site owner. '
    'The site owner is not liable for ad content. '
    '<a href="https://jenishestmoizavut.github.io/simulating-statistics/disclaimer.html" '
    'style="color:#8ab4f8;text-decoration:underline;">Read full disclaimer</a>'
)

MARKER = "ADSTERRA-DISCLAIMER-INJECTED"
SKIP_DIRS = {".git", "node_modules", ".github", "_site"}

# Slimmer, subtler bar: smaller text, tighter padding, a faint top border
# to separate it from page content, and the link styled to stand out
# without shouting. Still sits just above the 50px banner.
WRAPPER_TEMPLATE = """<!-- {marker} -->
<div style="position:fixed;left:0;right:0;bottom:50px;z-index:9998;
text-align:center;font-family:-apple-system,Segoe UI,Roboto,sans-serif;
font-size:10px;line-height:1.5;letter-spacing:0.1px;
color:#9a9a9a;background:rgba(15,15,15,0.92);
border-top:1px solid rgba(255,255,255,0.08);
padding:3px 10px;">
{text}
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

    wrapper = WRAPPER_TEMPLATE.format(marker=MARKER, text=DISCLAIMER_TEXT)

    pattern = re.compile(
        rf"<!-- {re.escape(MARKER)} -->.*?<!-- END {re.escape(MARKER)} -->\s*</body>",
        re.DOTALL
    )

    if pattern.search(content):
        new_content = pattern.sub(wrapper, content, count=1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return "replaced"

    if "</body>" not in content:
        return "no-body-tag"

    new_content = content.replace("</body>", wrapper, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return "updated"


def main():
    all_html = find_html_files(ROOT_DIR)
    if not all_html:
        print("No .html files found under", os.path.abspath(ROOT_DIR))
        return

    print(f"Found {len(all_html)} .html file(s). Injecting disclaimer footer...\n")
    updated, skipped_existing, skipped_no_body = 0, 0, 0
    for path in all_html:
        result = inject(path)
        if result in ("updated", "replaced"):
            print(f"{result}:  {path}")
            updated += 1
        elif result == "already-has-footer":
            print(f"skip (already has it): {path}")
            skipped_existing += 1
        elif result == "no-body-tag":
            print(f"skip (no </body> found): {path}")
            skipped_no_body += 1

    print(f"\nDone. {updated} updated/replaced, {skipped_existing} already had it, "
          f"{skipped_no_body} skipped (no </body> tag).")


if __name__ == "__main__":
    main()