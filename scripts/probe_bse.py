import urllib.request
import re

url = 'https://www.bseindia.com/assets/includenew/js/main-UOFMHHHR.js'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read().decode('utf-8', errors='ignore')
        print('JS length:', len(data))
        # Search for ListofScripData or download patterns
        for m in re.finditer(r'(ListofScripData|Download|Segment=Equity|ScripData)[^"\']{0,100}', data, re.IGNORECASE):
            print('Match:', m.group(0))
except Exception as e:
    print('Error:', e)
