import os
import re
import sys
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
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

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    embed_url = link + "?embed=1&mode=tme"

    print("🌐 Opening:", embed_url)

    driver.get(embed_url)

    time.sleep(8)

    folder = clean_filename(
        link.replace("https://", "").replace("/", "_")
    )

    os.makedirs(folder, exist_ok=True)

    found = False

    # -------------------------
    # VIDEO
    # -------------------------

    videos = driver.find_elements(By.TAG_NAME, "video")

    for i, video in enumerate(videos, start=1):

        src = video.get_attribute("src")

        if src and "cdn" in src:

            found = True

            print("🎬 Video:", src)

            download(
                src,
                os.path.join(folder, f"video_{i}.mp4")
            )

    # -------------------------
    # SOURCE TAGS
    # -------------------------

    sources = driver.find_elements(By.TAG_NAME, "source")

    for i, source in enumerate(sources, start=1):

        src = source.get_attribute("src")

        if src and "cdn" in src:

            found = True

            print("🎬 Source:", src)

            download(
                src,
                os.path.join(folder, f"source_video_{i}.mp4")
            )

    # -------------------------
    # REAL MEDIA IMAGES
    # -------------------------

    imgs = driver.find_elements(By.TAG_NAME, "img")

    img_count = 0

    for img in imgs:

        src = img.get_attribute("src")

        if not src:
            continue

        # skip avatars/thumbnails
        if "emoji" in src:
            continue

        if "photo" in src or "cdn" in src:

            img_count += 1
            found = True

            print("🖼 Image:", src)

            download(
                src,
                os.path.join(folder, f"image_{img_count}.jpg")
            )

    # -------------------------
    # CAPTION
    # -------------------------

    try:

        caption = driver.find_element(
            By.CLASS_NAME,
            "tgme_widget_message_text"
        ).text

        with open(
            os.path.join(folder, "caption.txt"),
            "w",
            encoding="utf-8"
        ) as f:

            f.write(caption)

        print("📝 Caption saved")

    except Exception:
        print("⚠️ No caption found")

    driver.quit()

    if not found:
        print("❌ No media found")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python download_telegram.py <link>")
        sys.exit(1)

    main(sys.argv[1])
