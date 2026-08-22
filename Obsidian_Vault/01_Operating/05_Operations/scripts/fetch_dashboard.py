import urllib.request

url = "http://100.106.235.103:8080/"
try:
    resp = urllib.request.urlopen(url, timeout=10)
    html = resp.read().decode()
    print(f"HTML length: {len(html)} chars")
    print(html[:8000])
except Exception as e:
    print(f"Error: {e}")