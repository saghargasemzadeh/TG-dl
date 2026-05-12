import os
import re
import sys
import requests
from bs4 import BeautifulSoup

def clean_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name.strip()

def download_file(url, output_folder):
    local_name = url.split("/")[-1].split("?")[0]
    local_name = clean_filename(local_name)

    path = os.path.join(output_folder, local_name)

    print(f"⬇️ Downloading: {url}")
    r = requests.get(url, stream=True)

    if r.status_code == 200:
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"✔ Saved: {path}")
    else:
        print(f"❌ Failed to download: {url}")

def download_from_telegram(link):
    if "t.me" not in link:
        print("❌ Invalid Telegram link")
        return

    # Try embed mode (best for scraping)
    embed_url = link + "?embed=1&mode=tme"

    print(f"🌐 Loading: {embed_url}")
    response = requests.get(embed_url)

    if response.status_code != 200:
        print("❌ Failed to load Telegram page.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Output folder (channel_message)
    folder_name = link.replace("https://", "").replace("/", "_")
    folder_name = clean_filename(folder_name)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    media_found = False

    # ----- IMAGES -----
    for img in soup.select("img"):
        src = img.get("src")
        if src and ("file" in src or "media" in src or "photo" in src):
            media_found = True
            download_file(src, folder_name)

    # ----- VIDEOS -----
    for video in soup.select("video"):
        src = video.get("src")
        if src:
            media_found = True
            download_file(src, folder_name)

    # ----- DOCUMENTS -----
    for a in soup.select("a"):
        href = a.get("href")
        if href and ("file" in href or "media" in href or "document" in href):
            media_found = True
            download_file(href, folder_name)

    if not media_found:
        print("⚠️ No media found in this post.")
    else:
        print("🎉 Download completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_telegram.py <telegram_link>")
        sys.exit(1)

    download_from_telegram(sys.argv[1])
