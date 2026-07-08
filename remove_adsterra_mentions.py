#!/usr/bin/env python3
"""
Removes all literal mentions of "Adsterra" (any casing) from every HTML
file in the repo — marker comments, disclaimer text, localStorage keys —
replacing them with neutral generic wording, per AdSterra's compliance
requirement to not publicly name them on your site.

USAGE:
1. cd into your repo root:
   cd simulating-statistics

2. Run:
   python remove_adsterra_mentions.py

3. Check with `git diff --stat`, eyeball a page or two, then:
   git add -A
   git commit -m "Remove public AdSterra mentions per their compliance policy"
   git push

4. IMPORTANT: also manually check disclaimer.html and update
   fix_ads_and_disclaimer.py's own constants (see note printed at the end).
"""

import os

ROOT_DIR = ".."
SKIP_DIRS = {".git", "node_modules", ".github", "_site"}

# Order matters: do longer/more specific strings first so shorter ones
# don't partially clobber them.
REPLACEMENTS = [
    ("ADSTERRA-BANNER-INJECTED", "AD-BANNER-INJECTED"),
    ("ADSTERRA-DISCLAIMER-INJECTED", "AD-DISCLAIMER-INJECTED"),
    ("ADSTERRA-FOOTER-LINK-INJECTED", "AD-FOOTER-LINK-INJECTED"),
    ("adsterraDisclaimerDismissed", "adDisclaimerDismissed"),
    ("AdSterra", "our ad partner"),
    ("Adsterra", "our ad partner"),
    ("ADSTERRA", "AD-NETWORK"),
]


def find_html_files(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith((".html", ".htm")):
                found.append(os.path.join(dirpath, name))
    return found


def process(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return "updated"
    return "unchanged"


def main():
    all_html = find_html_files(ROOT_DIR)
    if not all_html:
        print("No .html files found under", os.path.abspath(ROOT_DIR))
        return

    print(f"Found {len(all_html)} .html file(s). Scrubbing AdSterra mentions...\n")
    updated, unchanged = 0, 0
    for path in all_html:
        result = process(path)
        if result == "updated":
            print(f"updated:  {path}")
            updated += 1
        else:
            unchanged += 1

    print(f"\nDone. {updated} updated, {unchanged} unchanged.")
    print("\n!! REMINDER: also open disclaimer.html manually and check the body "
          "text doesn't name AdSterra directly (this script only catches exact "
          "string matches, not paraphrased mentions).")
    print("!! Also update the constants inside fix_ads_and_disclaimer.py to use "
          "AD-BANNER-INJECTED / AD-DISCLAIMER-INJECTED / AD-FOOTER-LINK-INJECTED "
          "and the reworded disclaimer text, so future re-runs stay consistent.")


if __name__ == "__main__":
    main()