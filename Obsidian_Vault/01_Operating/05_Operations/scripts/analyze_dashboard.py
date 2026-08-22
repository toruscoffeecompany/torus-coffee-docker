import urllib.request

url = "http://100.83.247.14:8080/"
resp = urllib.request.urlopen(url, timeout=10)
html = resp.read().decode()

# Find the tab structure
print(f"Dashboard HTML: {len(html)} chars")
print()

# Look for tab links, iframe srcs, and data attributes
import re

# Find all iframe srcs
iframes = re.findall(r'<iframe[^>]+src="([^"]*)"', html)
print(f"iFrames ({len(iframes)}):")
for f in iframes[:10]:
    print(f"  {f}")

# Find all data attributes that might indicate tab structure
data_attrs = re.findall(r'data-[a-z]+="([^"]*)"', html)
print(f"\nData attributes: {data_attrs[:10]}")

# Find tab-related elements
tab_patterns = re.findall(r'(tab-[a-z_]+|[a-z_]+-tab|data-tab="[^"]*"|id="tab-[a-z_]+"|href="#tab-[a-z_]+"|href="#!/[a-z_]+")', html)
print(f"\nTab patterns: {list(set(tab_patterns))[:10]}")

# Find link hrefs that look like tabs
hrefs = re.findall(r'href="(#!/[^\"]*|#[a-z_]+)"', html)
print(f"\nHash hrefs: {list(set(hrefs))[:15]}")

# Find nav/list items
nav_items = re.findall(r'<li[^>]*>([^<]+)</li>', html[:10000])
print(f"\nNav items: {nav_items[:15]}")

# Find script sources
scripts = re.findall(r'src="([^"]+\.js)"', html)
print(f"\nScripts: {scripts[:10]}")

# Find the section of HTML around 'augur' (case insensitive)
augur_matches = [(m.start(), html[m.start():m.start()+200]) for m in re.finditer('augur', html, re.IGNORECASE)]
print(f"\nAugur mentions: {len(augur_matches)}")
for pos, context in augur_matches[:5]:
    print(f"  At {pos}: {context[:100]}")

# Find sections with 'tab' class
tab_sections = re.findall(r'class="[^"]*tab[^"]*"[^>]*>([^<]+)', html)
print(f"\nTab class sections: {tab_sections[:10]}")

# Find the main content structure
content_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
if content_match:
    content = content_match.group(1)[:2000]
    print(f"\nMain content preview: {content[:500]}")