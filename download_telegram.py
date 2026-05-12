import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import hashlib
import random
import string

def clean_filename(name, max_len=50):
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    if len(name) > max_len:
        ext = ""
        if "." in name:
            ext = "." + name.split(".")[-1]
        hash_part = hashlib.md5(name.encode()).hexdigest()[:10]
        name = name[:20] + "_" + hash_part + ext
    return name.strip()

def random_name(ext=""):
    rand = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return rand + ext

def download_file(url, output_folder):
    # استخراج فرمت فایل
    ext = ""
    filename = url.split("/")[-1].split("?")[0]
    if "." in filename:
        ext = "." + filename.split(".")[-1]

    safe_name = clean_filename(filename)

    # اگر هنوز هم طولانی بود، اسم رندوم بده
    if len(safe_name) > 60:
        safe_name = random_name(ext)

    path = os.path.join(output_folder, safe_name)

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

    embed_url = link + "?embed=1&mode=tme"
    print(f"🌐 Loading: {embed_url}")

    response = requests.get(embed_url)

    if response.status_code != 200:
        print("❌ Failed to load Telegram page.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    folder_name = link.replace("https://", "").replace("/", "_")
    folder_name = clean_filename(folder_name)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    media_found = False

    # Images
    for img in soup.select("img"):
        src = img.get("src")
        if src and "file" in src:
            media_found = True
            download_file(src, folder_name)

    # Videos
    for video in soup.select("video"):
        src = video.get("src")
        if src:
            media_found = True
            download_file(src, folder_name)

    # Documents
    for a in soup.select("a"):
        href = a.get("href")
        if href and "file" in href:
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
