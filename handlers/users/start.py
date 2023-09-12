from aiogram import types
from keyboards.default import keyboard_menu
from loader import dp
from filters import IsAdmin
from keyboards.inline.inline_kb_menu import *
from keyboards.default.keyboard_menu import *
from utils.db_api.db_asyncpg import *
from data.config import *
from filters import IsAdmin


@dp.message_handler(IsAdmin(), commands=['start'])
async def command_start_admin(message: types.Message) -> None:
    await message.answer(f'Здравствуйте, {message.from_user.full_name},  вы попали в админ панель!',
                         reply_markup=keyboard_menu.admin)


@dp.message_handler(commands='start')
async def command_start(message: types.Message) -> None:
    exists = await user_exists(message.from_user.id)
    if not exists:
        await message.answer(f'Приветсвую!👋 \n'
                             f'Для того чтобы начать пользоваться ботом подтвердите ваш номер',
                             reply_markup=keyboard_menu.phone,
                             parse_mode="HTML")
    else:
        await message.answer('Воспользуйтесь кнопками ниже', reply_markup=keyboard_menu.main)


@dp.message_handler(commands='chatid')
async def send_chatid(message: types.Message) -> None:
    await message.answer(message.chat.id)

