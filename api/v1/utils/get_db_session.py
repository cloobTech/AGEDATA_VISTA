from storage import db


async def get_db_session():
    """Get DB Instance"""
    try:
        yield db
    except Exception as e:
        await db.rollback()
        raise e
    finally:
        print("Shutting down DB")
        # await db.shutdown_db()
