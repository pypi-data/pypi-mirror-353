import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO
from tqdm import tqdm

# Supported formats
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"]

def is_image_url(url):
    return any(url.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)

def get_image_size(url):
    try:
        response = requests.get(url, timeout=5)
        image = Image.open(BytesIO(response.content))
        return image.size, len(response.content)
    except Exception:
        return (0, 0), 0

def scrape_images(url, download_dir="downloaded_images"):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Create download directory
    os.makedirs(download_dir, exist_ok=True)

    image_tags = soup.find_all("img")
    image_links = []

    for img in image_tags:
        src = img.get("src") or img.get("data-src") or ""
        full_url = urljoin(url, src)
        if is_image_url(full_url):
            image_links.append(full_url)

    print(f"Found {len(image_links)} image(s). Measuring quality...")

    # Measure and sort by resolution or size
    scored_images = []
    for img_url in tqdm(image_links, desc="Analyzing"):
        (width, height), file_size = get_image_size(img_url)
        score = width * height or file_size
        scored_images.append((score, img_url))

    scored_images.sort(reverse=True)  # Best quality first

    print("Downloading images...")

    for idx, (_, img_url) in enumerate(scored_images, 1):
        try:
            img_data = requests.get(img_url, headers=headers).content
            filename = os.path.join(download_dir, f"image_{idx}" + os.path.splitext(img_url)[-1].split("?")[0])
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

    print("Done!")

# Example usage

    target_url = input("Enter a website URL: ").strip()
    scrape_images(target_url)
