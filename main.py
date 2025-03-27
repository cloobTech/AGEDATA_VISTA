from utils.email_service import send_email
from storage import DBStorage as DB
import asyncio


db = DB()


async def reload_db():
    """reload"""
    await db.drop_all()
    await db.reload()
    print('DB reloaded')

# asyncio.run(reload_db())

context = {
    'verification_code': '123456'
}


async def send_verification_email():
    await send_email("belkid98@gmail.com", "Verify your email", template_name="verification_email.html", context=context)

asyncio.run(send_verification_email())
