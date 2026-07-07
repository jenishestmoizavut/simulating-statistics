#!/usr/bin/env python3
"""
Adds a small disclaimer footer to every page of the site, noting that
the ads are served by AdSterra, are not personally endorsed, and that
you (the site owner) should not be held liable for their content.

USAGE:
1. Clone your repo (if you haven't already):
   git clone https://github.com/jenishestmoizavut/simulating-statistics.git
   cd simulating-statistics

2. Adjust DISCLAIMER_TEXT below if you want to reword it.

3. Put this script in the repo root and run:
   python add_disclaimer_footer.py

4. Check with `git diff`, open a couple of pages locally to eyeball it,
   then:
   git add -A
   git commit -m "Add AdSterra disclaimer footer to all pages"
   git push
"""

import os
import re

ROOT_DIR = "."

DISCLAIMER_TEXT = (
    "Ads on this site are served by AdSterra and are not personally "
    "endorsed by the site owner. The site owner is not responsible or "
    "liable for the content of any ads shown. Read the full at https://jenishestmoizavut.github.io/attrack/disclaimer.html"
)

MARKER = "ADSTERRA-DISCLAIMER-INJECTED"
SKIP_DIRS = {".git", "node_modules", ".github", "_site"}

# This footer sits above the fixed banner (which is 50px tall), so it
# doesn't get covered by it. Adjust bottom offset if you change the
# banner height.
WRAPPER_TEMPLATE = """<!-- {marker} -->
<div style="position:fixed;left:0;right:0;bottom:50px;z-index:9998;
text-align:center;font-family:sans-serif;font-size:11px;line-height:1.4;
color:#ccc;background:rgba(0,0,0,0.7);padding:4px 8px;">
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

    # Pattern matches everything from the opening marker comment
    # through the closing marker comment + </body>
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

    print(f"\nDone. {updated} updated, {skipped_existing} already had it, "
          f"{skipped_no_body} skipped (no </body> tag).")


if __name__ == "__main__":
    main()