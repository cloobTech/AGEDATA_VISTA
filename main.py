from services.projects.project import create_project
from services.projects.project_member import add_project_member
from services.auth.local_auth import register_user
from storage import DBStorage as DB
import asyncio

db = DB()


async def reload_db():
    """reload"""
    await db.drop_all()
    await db.reload()
    print('DB reloaded')

asyncio.run(reload_db())


async def create_multiple_users():
    """Create multiple users"""
    users = [
        {
            "id": "1",
            "email": "test@gmai1.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Doe",
            "email_verified": True,
            "role": "user"

        },
        {
            "id": "2",
            "email": "test@gmai2.com",
            "password": "password",
            "first_name": "Jane",
            "last_name": "Doe",
            "email_verified": True,
            "role": "user"
        },
        {
            "id": "3",
            "email": "test@gmai3.com",
            "password": "password",
            "first_name": "James",
            "last_name": "Doe",
            "email_verified": True,
            "role": "user"
        }
    ]

    # create a project
    project = {
        "id": "1",
        "title": "Test Project",
        "description": "This is a test project",
        "owner_id": "1"
    }

    for user in users:
        await register_user(user, db, None)
        if user.get('id') == '1':
            # await db.merge(user)
            x = await create_project(project, db)

asyncio.run(create_multiple_users())

# # add users to a project
# data = {
#     "project_id": "1",
#     "user_id": "2"
# }

# asyncio.run(add_project_member(data, db))


