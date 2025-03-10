import aiohttp


async def fetch_cloudinary_file(url: str) -> bytes:
    """
    Fetches a file from Cloudinary and returns its content as bytes.

    Args:
        url (str): The Cloudinary file URL.

    Returns:
        bytes: The file content.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()  # Return binary content
            else:
                raise Exception(
                    f"Failed to fetch file. HTTP Status: {response.status}")
