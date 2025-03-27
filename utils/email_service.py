import asyncio
import yagmail
from settings.pydantic_config import settings
from premailer import transform
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))


async def send_email(to, subject, template_name=None, context: dict = None):
    """Email Service"""
    yag = yagmail.SMTP(settings.EMAIL_CONFIG_USERNAME,
                       settings.EMAIL_CONFIG_PASSWORD)

    try:
        template = env.get_template(template_name) if template_name else None
        if template:
            html_content = template.render(
                **context) if context else html_content
        contents = transform(html_content)
        await asyncio.to_thread(
            yag.send,
            to=to,
            subject=subject,
            contents=contents
        )
        print("Email sent successfully")
    except Exception as e:
        raise Exception(f'Failed to send email, {e}') from e
    return {"status": "Email sent successfully"}
