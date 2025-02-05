# from storage import DBStorage as DB
# import asyncio

# db = DB()


# async def reload_db():
#     """reload"""
#     await db.drop_all()
#     await db.reload()
#     print('DB reloaded')

# asyncio.run(reload_db())


class Person:
    def __init__(self, name, age, **t):
        self.name = name
        self.age = age

        if t:
            for key, val in t.items():
                setattr(self, key, val) 


p1 = Person ("olamide", 31)
p2 = Person ("Dorcas", 26, gender="female", colour = "blue")

print(p1.__dict__)
print(p2.__dict__)