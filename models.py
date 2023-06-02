import datetime

from pony.orm import Database, Required
from config import DB_CONFIG

# psql \! chcp 1251 - смена кодировки
db = Database()
db.bind(**DB_CONFIG)
# set_sql_debug(True)


class TikTokMovies(db.Entity):
    link = Required(str)
    is_active = Required(bool)


class PhotoMem(db.Entity):
    link = Required(str)
    width = Required(int)
    height = Required(int)
    is_active = Required(bool, sql_default=True)


class Greeting(db.Entity):
    text = Required(str)
    is_active = Required(bool, sql_default=True)


class UserBot(db.Entity):
    user_id = Required(int)
    status = Required(str)
    ripple_status = Required(bool)
    ripple_time = Required(datetime.datetime)


db.generate_mapping(create_tables=True)
