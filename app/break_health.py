import urllib.request


req = urllib.request.Request("http://localhost:8000/admin/break-health", method="POST")

print(urllib.request.urlopen(req).read().decode())