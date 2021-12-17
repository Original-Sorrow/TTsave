
from peewee import *


db = SqliteDatabase('db/users.sqlite')

class Users(Model):
    id = PrimaryKeyField()
    
    class Meta:
        database=db

with db:
    db.create_tables([Users])

def new_user(_id):
    with db:
        if not Users.select(1).where(Users.id == _id).exists():
            Users.create(id=_id)


async def to_all(message,markup):
    with db:
        for user in Users.select(Users.id):
            await message.copy_to(user.id,reply_markup=markup)
        return len(Users.select(Users.id))

def stata():
    with db:
        return len(Users.select(Users.id))
