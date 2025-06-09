import os
import tempfile
import requests
from urllib.parse import urlparse

def download_image_from_url(url, target_dir):
    """Download image from URL to target directory"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Extract filename from URL
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    filepath = os.path.join(target_dir, filename)
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return filepath