import json
import sys
import time
import urllib.request

url = sys.argv[1] if len(sys.argv) > 1 else "http://backend/"

while True:
    try:
        data=json.load(urllib.request.urlopen(url, timeout=2))
        print(f"version={data['version']}  pod={data['pod']}", flush=True)
    except Exception as exc:
        print(f"ERROR {exc}", flush=True)
    time.sleep(0.5)