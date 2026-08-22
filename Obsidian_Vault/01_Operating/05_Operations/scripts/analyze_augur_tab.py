import urllib.request, re

url = "http://100.83.247.14:8080/"
resp = urllib.request.urlopen(url, timeout=10)
html = resp.read().decode()

# Find the section around the Augur tab
augur_pos = html.find('augur-trading')
print(f"Augur tab found at position: {augur_pos}")

# Get context around it
start = max(0, augur_pos - 500)
end = min(len(html), augur_pos + 3000)
section = html[start:end]
print("\n=== HTML around Augur tab ===")
print(section)

# Find all tabnav links
tabnav_links = re.findall(r'<a href="([^"]*)" class="tabnav-link">([^<]+)</a>', html)
print("\n=== All tabnav links ===")
for url_part, label in tabnav_links:
    print(f"  {label.strip()}: {url_part}")

# Find any embed or content containers
print("\n=== Looking for content containers ===")
# Look for iframe, embed, or div with id matching tab names
for match in re.finditer(r'(?:id|class)="([^"]*(?:augur|sandbox)[^"]*)"', html):
    print(f"  Found: {match.group(0)}")

# Look for any JS that loads tab content
js_sections = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for js in js_sections:
    if 'augur' in js.lower() or 'tab' in js.lower() or 'iframe' in js.lower():
        print(f"\n=== JS with augur/tab/iframe ===")
        print(js[:1000])