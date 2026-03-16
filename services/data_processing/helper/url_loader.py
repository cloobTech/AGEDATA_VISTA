"""
URL-based dataset ingestion.
Supports: direct CSV/Excel URLs, Kaggle, GitHub raw files, Google Drive, S3, Dropbox, HuggingFace.
"""
import os
import io
import re
import logging
import asyncio
from typing import Optional, Tuple
import httpx
import pandas as pd

log = logging.getLogger(__name__)

MAX_SIZE_MB = 500
TIMEOUT = 120


async def load_dataframe_from_url(url: str) -> Tuple[pd.DataFrame, str]:
    """
    Load a pandas DataFrame from any supported URL.
    Returns (DataFrame, detected_filename).
    Raises ValueError with a clear message on failure.
    """
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")

    if 'kaggle.com' in url:
        return await _load_kaggle(url)
    elif 'github.com' in url and 'raw' not in url:
        url = _github_to_raw(url)
        return await _load_direct(url)
    elif 'drive.google.com' in url:
        url = _gdrive_to_direct(url)
        return await _load_direct(url)
    elif 'dropbox.com' in url:
        url = _dropbox_to_direct(url)
        return await _load_direct(url)
    elif url.startswith('s3://') or 'amazonaws.com' in url:
        return await _load_s3(url)
    elif 'huggingface.co' in url:
        return await _load_huggingface(url)
    else:
        return await _load_direct(url)


async def _load_direct(url: str) -> Tuple[pd.DataFrame, str]:
    """Download and parse a direct file URL."""
    log.info("Fetching dataset from: %s", url)

    async with httpx.AsyncClient(
        timeout=TIMEOUT,
        follow_redirects=True,
        headers={'User-Agent': 'AgeDataVista/1.0 DataLoader'},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    content_length = len(response.content)
    size_mb = content_length / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise ValueError(
            f"File is too large: {size_mb:.1f}MB. "
            f"Maximum allowed: {MAX_SIZE_MB}MB. "
            f"Use Big Data analysis for files over {MAX_SIZE_MB}MB."
        )

    filename = _extract_filename(url, response.headers)
    df = _parse_content(response.content, filename)
    log.info("Loaded %d rows x %d cols from %s", len(df), len(df.columns), url)
    return df, filename


async def _load_kaggle(url: str) -> Tuple[pd.DataFrame, str]:
    """Load from Kaggle. Tries API credentials first, then direct URL."""
    kaggle_username = os.getenv('KAGGLE_USERNAME')
    kaggle_key = os.getenv('KAGGLE_KEY')

    if kaggle_username and kaggle_key:
        try:
            return await _load_kaggle_api(url, kaggle_username, kaggle_key)
        except Exception as e:
            log.warning("Kaggle API failed: %s. Trying direct URL.", e)

    if '/datasets/' in url and not any(url.endswith(ext) for ext in ('.csv', '.xlsx', '.xls', '.json', '.zip')):
        raise ValueError(
            "To download from Kaggle:\n"
            "1. Go to the dataset page on Kaggle\n"
            "2. Click the download icon next to the specific CSV file\n"
            "3. Copy the direct download URL\n"
            "OR set KAGGLE_USERNAME and KAGGLE_KEY environment variables "
            "for automatic API access.\n"
            f"Dataset URL: {url}"
        )

    return await _load_direct(url)


async def _load_kaggle_api(url: str, username: str, key: str) -> Tuple[pd.DataFrame, str]:
    """Download from Kaggle using API credentials."""
    try:
        import kaggle
    except ImportError:
        raise ValueError("kaggle package not installed. Run: pip install kaggle")

    match = re.search(r'kaggle\.com/datasets/([^/]+)/([^/?]+)', url)
    if not match:
        raise ValueError(f"Cannot parse Kaggle dataset URL: {url}")

    owner, dataset = match.group(1), match.group(2)
    dataset_id = f"{owner}/{dataset}"

    import tempfile
    import glob as _glob
    with tempfile.TemporaryDirectory() as tmpdir:
        kaggle.api.dataset_download_files(
            dataset_id, path=tmpdir, unzip=True, quiet=True
        )
        csv_files = _glob.glob(os.path.join(tmpdir, '*.csv'))
        if not csv_files:
            csv_files = _glob.glob(os.path.join(tmpdir, '*.xlsx'))
        if not csv_files:
            raise ValueError(f"No CSV/Excel files found in Kaggle dataset {dataset_id}")

        csv_file = max(csv_files, key=os.path.getsize)
        filename = os.path.basename(csv_file)
        with open(csv_file, 'rb') as f:
            df = _parse_content(f.read(), filename)
        return df, filename


async def _load_huggingface(url: str) -> Tuple[pd.DataFrame, str]:
    """Load from HuggingFace datasets."""
    if '/blob/' in url:
        url = url.replace('/blob/', '/resolve/')

    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    headers = {}
    if hf_token:
        headers['Authorization'] = f'Bearer {hf_token}'

    async with httpx.AsyncClient(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    filename = _extract_filename(url, response.headers)
    df = _parse_content(response.content, filename)
    return df, filename


async def _load_s3(url: str) -> Tuple[pd.DataFrame, str]:
    """Load from AWS S3 public buckets."""
    if url.startswith('s3://'):
        parts = url[5:].split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        url = f"https://{bucket}.s3.amazonaws.com/{key}"

    return await _load_direct(url)


def _github_to_raw(url: str) -> str:
    return (url
            .replace('github.com', 'raw.githubusercontent.com')
            .replace('/blob/', '/'))


def _gdrive_to_direct(url: str) -> str:
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    return url


def _dropbox_to_direct(url: str) -> str:
    return url.replace('?dl=0', '?dl=1').replace('www.dropbox.com', 'dl.dropboxusercontent.com')


def _extract_filename(url: str, headers) -> str:
    cd = headers.get('content-disposition', '') if headers else ''
    if cd:
        match = re.search(r'filename[^;=\n]*=([\'""]?)(.+?)\1', cd)
        if match:
            return match.group(2)

    path = url.split('?')[0]
    name = path.split('/')[-1]
    if '.' in name:
        return name
    return 'dataset.csv'


def _parse_content(content: bytes, filename: str) -> pd.DataFrame:
    """Parse bytes content into DataFrame based on filename extension."""
    fname_lower = filename.lower()
    buf = io.BytesIO(content)

    if fname_lower.endswith('.csv') or fname_lower.endswith('.tsv'):
        sep = '\t' if fname_lower.endswith('.tsv') else None
        try:
            return pd.read_csv(buf, sep=sep, engine='python')
        except Exception:
            buf.seek(0)
            return pd.read_csv(buf, sep=None, engine='python', on_bad_lines='skip')

    elif fname_lower.endswith(('.xlsx', '.xls')):
        return pd.read_excel(buf)

    elif fname_lower.endswith(('.json', '.jsonl')):
        text = content.decode('utf-8', errors='replace')
        try:
            import json
            data = json.loads(text)
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list) and len(val) > 0:
                        return pd.DataFrame(val)
                return pd.DataFrame([data])
        except Exception:
            buf.seek(0)
            return pd.read_json(buf, lines=True)

    elif fname_lower.endswith('.parquet'):
        return pd.read_parquet(buf)

    elif fname_lower.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(buf) as z:
            csv_files = [f for f in z.namelist()
                         if f.endswith(('.csv', '.tsv', '.xlsx'))]
            if not csv_files:
                raise ValueError("ZIP file contains no CSV/Excel files")
            largest = max(csv_files, key=lambda f: z.getinfo(f).file_size)
            with z.open(largest) as f:
                return _parse_content(f.read(), largest)

    else:
        try:
            return pd.read_csv(buf, sep=None, engine='python')
        except Exception:
            raise ValueError(
                f"Cannot parse file format: {filename}. "
                f"Supported formats: CSV, TSV, Excel, JSON, Parquet, ZIP"
            )


async def _get_url_info(url: str) -> dict:
    """Get file info from URL without downloading full content."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.head(url)
            content_type = response.headers.get('content-type', '')
            content_length = int(response.headers.get('content-length', 0))
            filename = _extract_filename(url, response.headers)
            return {
                'accessible': True,
                'filename': filename,
                'size_mb': round(content_length / (1024 * 1024), 2),
                'content_type': content_type,
                'url': url,
            }
    except Exception as e:
        return {'accessible': False, 'error': str(e), 'url': url}


def get_url_preview(url: str) -> dict:
    """Synchronous version for quick URL validation."""
    return asyncio.run(_get_url_info(url))
