from json import dump, load
from pathlib import Path
from time import monotonic, sleep

from httpx import Client

# makes a client
client = Client()
headers = {
        "user-agent": "Boilercrib-scraper/1.0 (https://github.com/Purdue-ACM-SIGAPP/boilercrib-scraper)",
        }
last_request_time = 0
MIN_DELAY = 60
CACHE_FILE = Path(__file__).resolve().parent/"cache.json"
cache = {}
# if there is a cache load data from cache first
try:
    with open(CACHE_FILE, "r") as f:
        cache = load(f)
except FileNotFoundError:
    print("No cache file, making one.")

def fetch(url):
    global last_request_time

    if url in cache:
        return cache[url]
    else:
        if monotonic() - last_request_time <= MIN_DELAY:
            sleep(MIN_DELAY - (monotonic() - last_request_time))
        last_request_time = monotonic()
        res = client.get(url, headers=headers)
        res.raise_for_status()
        cache[url] = res.text
        writeCache()
        return res.text

# helper function that writes the dictionary to a temp file first before moving it to the json file so that if the write crashes the original data is safe
def writeCache():
    with open(CACHE_FILE.with_suffix(".tmp"), "w") as f:
        dump(cache, f)
    tempPath = CACHE_FILE.with_suffix(".tmp")
    tempPath.replace(CACHE_FILE)
