# import asyncio
from pathlib import Path
import asyncio
import yagmail
from settings.pydantic_config import settings
# from jinja2 import Environment, FileSystemLoader
# from typing import Callable


async def send_email(to, subject, template_name, context=None):
    """Email Service"""
    yag = yagmail.SMTP(settings.EMAIL_CONFIG_USERNAME,
                       settings.EMAIL_CONFIG_PASSWORD)

    # Adjust the path according to your project structure
    templates_dir = Path(__file__).parent.parent / 'templates'

    try:
        template_path = templates_dir / template_name
        with open(template_path, 'r', encoding='utf-8') as file:
            contents = file.read()
        # If you have placeholders in your template, you can replace them with actual values from context
        if context:
            contents = contents.format(**context)
        await asyncio.to_thread(
            yag.send,
            to=to,
            subject=subject,
            contents=contents
        )
    except Exception as e:
        raise Exception(f'Failed to send email, {e}') from e
    return {"status": "Email sent successfully"}
