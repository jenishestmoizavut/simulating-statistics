#!/usr/bin/env python3
"""
ONE-TIME cleanup: removes every known variant of ad/disclaimer/footer-link
blocks (old ADSTERRA- names, AD- names, ads- names, orphans) from every
HTML file, then inserts exactly one clean, consistently-named set.

Run once from repo root: python cleanup_all_ad_blocks.py
Then: git diff --stat, eyeball a page, git add -A, git commit, git push
"""
import os, re

ROOT_DIR = "."
SKIP_DIRS = {".git", "node_modules", ".github", "_site"}

# Every marker name variant that has ever existed in this repo's history
MARKER_VARIANTS = {
    "BANNER":      ["ADSTERRA-BANNER-INJECTED", "AD-BANNER-INJECTED", "ads-BANNER-INJECTED"],
    "DISCLAIMER":  ["ADSTERRA-DISCLAIMER-INJECTED", "AD-DISCLAIMER-INJECTED", "ads-DISCLAIMER-INJECTED"],
    "FOOTER_LINK": ["ADSTERRA-FOOTER-LINK-INJECTED", "AD-FOOTER-LINK-INJECTED", "ads-FOOTER-LINK-INJECTED"],
}

# Final, permanent naming scheme going forward (all consistent, all uppercase AD-)
BANNER_MARKER = "AD-BANNER-INJECTED"
DISCLAIMER_MARKER = "AD-DISCLAIMER-INJECTED"
FOOTER_LINK_MARKER = "AD-FOOTER-LINK-INJECTED"

AD_SNIPPET = """
<script>
  if (typeof atAsyncOptions !== 'object') var atAsyncOptions = [];
  atAsyncOptions.push({
    key: '00244a2b0b21b7020f7519a5319093fa',
    format: 'js',
    async: true,
    container: 'atContainer-00244a2b0b21b7020f7519a5319093fa',
    params: {},
  });
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.async = true;
  script.src = 'https://www.highperformanceformat.com/00244a2b0b21b7020f7519a5319093fa/invoke.js';
  document.getElementsByTagName('head')[0].appendChild(script);
</script>
<div id="atContainer-00244a2b0b21b7020f7519a5319093fa"></div>
"""
DISCLAIMER_TEXT = (
    'Ads are served by our ad partner and not personally endorsed. Not liable for ad content. '
    '<a href="https://jenishestmoizavut.github.io/simulating-statistics/disclaimer.html" '
    'style="color:#8ab4f8;text-decoration:underline;">Full disclaimer</a>'
)

BANNER_BLOCK = f"""<!-- {BANNER_MARKER} -->
<div style="position:fixed;left:0;right:0;bottom:0;z-index:9999;
display:flex;justify-content:center;align-items:center;
width:320px;height:50px;margin:0 auto;background:rgba(0,0,0,0.85);">
<span style="position:absolute;top:-13px;left:0;font-size:9px;
font-family:sans-serif;color:#aaa;background:#111;
padding:1px 5px;border-radius:2px 2px 0 0;letter-spacing:0.5px;">Ad</span>
{AD_SNIPPET}
</div>
<!-- END {BANNER_MARKER} -->"""

DISCLAIMER_BLOCK = f"""<!-- {DISCLAIMER_MARKER} -->
<div id="ad-disclaimer" style="position:fixed;left:0;right:0;bottom:50px;z-index:9998;
display:flex;align-items:center;justify-content:center;gap:8px;
font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:10px;
line-height:1.4;color:#9a9a9a;background:rgba(15,15,15,0.92);
border-top:1px solid rgba(255,255,255,0.08);padding:3px 28px 3px 10px;">
<span>{DISCLAIMER_TEXT}</span>
<button onclick="document.getElementById('ad-disclaimer').style.display='none';
localStorage.setItem('adDisclaimerDismissed','1');"
style="position:absolute;right:6px;background:none;border:none;color:#888;
font-size:13px;cursor:pointer;line-height:1;padding:2px 4px;">&#10005;</button>
</div>
<script>
if (localStorage.getItem('adDisclaimerDismissed') === '1') {{
  document.addEventListener('DOMContentLoaded', function() {{
    var el = document.getElementById('ad-disclaimer');
    if (el) el.style.display = 'none';
  }});
}}
</script>
<!-- END {DISCLAIMER_MARKER} -->"""

FOOTER_LINK_BLOCK = f"""<!-- {FOOTER_LINK_MARKER} -->
<div style="text-align:center;font-family:-apple-system,Segoe UI,Roboto,sans-serif;
font-size:10px;color:#666;padding:16px 10px 70px;">
<a href="https://jenishestmoizavut.github.io/simulating-statistics/disclaimer.html"
style="color:#666;text-decoration:underline;">Ad Disclaimer</a>
</div>
<!-- END {FOOTER_LINK_MARKER} -->"""


def find_html_files(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith((".html", ".htm")):
                found.append(os.path.join(dirpath, name))
    return found


def strip_all_variants(content, marker_list):
    for marker in marker_list:
        pattern = re.compile(
            rf"\s*<!-- {re.escape(marker)} -->.*?<!-- END {re.escape(marker)} -->",
            re.DOTALL
        )
        content = pattern.sub("", content)
    return content


def process(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if "</body>" not in content:
        return "no-body-tag"

    original = content
    for group in MARKER_VARIANTS.values():
        content = strip_all_variants(content, group)

    insertion = f"{BANNER_BLOCK}\n{DISCLAIMER_BLOCK}\n{FOOTER_LINK_BLOCK}\n</body>"
    content = content.replace("</body>", insertion, 1)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return "updated"
    return "unchanged"


def main():
    all_html = find_html_files(ROOT_DIR)
    updated, unchanged, no_body = 0, 0, 0
    for path in all_html:
        result = process(path)
        if result == "updated":
            print(f"updated:  {path}")
            updated += 1
        elif result == "unchanged":
            unchanged += 1
        else:
            print(f"skip (no </body>): {path}")
            no_body += 1
    print(f"\nDone. {updated} updated, {unchanged} unchanged, {no_body} skipped.")


if __name__ == "__main__":
    main()