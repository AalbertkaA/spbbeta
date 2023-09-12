from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from utils.db_api.db_asyncpg import status


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.id in [i['user_id'] for i in await status()]



