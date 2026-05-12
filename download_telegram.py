import os
import re
import sys
import time
import requests

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def download(url, path):
    r = requests.get(url, stream=True)

    if r.status_code == 200:
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        print("✅ Downloaded:", path)
    else:
        print("❌ Failed:", url)


def main(link):
    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    embed_url = link + "?embed=1&mode=tme"

    print("🌐 Opening:", embed_url)

    driver.get(embed_url)

    time.sleep(5)

    html = driver.page_source

    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    folder = clean_filename(
        link.replace("https://", "").replace("/", "_")
    )

    os.makedirs(folder, exist_ok=True)

    # ------------------------
    # Caption
    # ------------------------

    caption = ""

    desc = soup.find("meta", {"property": "og:description"})

    if desc:
        caption = desc.get("content", "")

        with open(os.path.join(folder, "caption.txt"), "w", encoding="utf-8") as f:
            f.write(caption)

        print("📝 Caption saved")

    # ------------------------
    # VIDEO
    # ------------------------

    videos = soup.find_all("video")

    found = False

    for i, video in enumerate(videos, start=1):

        src = video.get("src")

        if src:
            found = True

            path = os.path.join(folder, f"video_{i}.mp4")

            print("🎬 Video found:", src)

            download(src, path)

    # ------------------------
    # IMAGE
    # ------------------------

    imgs = soup.find_all("img")

    for i, img in enumerate(imgs, start=1):

        src = img.get("src")

        if src and "telesco.pe/file/" in src:

            # thumbnail/channel photo skip
            if "emoji" in src:
                continue

            path = os.path.join(folder, f"image_{i}.jpg")

            print("🖼 Image found:", src)

            download(src, path)

            found = True

    if not found:
        print("⚠️ No media found")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python download_telegram.py <link>")
        sys.exit(1)

    main(sys.argv[1])
