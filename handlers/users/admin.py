from aiogram.dispatcher.filters import Command
from aiogram import types
from aiogram.types import InputFile, ReplyKeyboardRemove, CallbackQuery
from loader import dp
from keyboards.default import keyboard_menu
from keyboards.inline import inline_kb_menu
from filters import IsAdmin


@dp.message_handler(IsAdmin(), text='/admin')
async def adminPanel(message: types.Message):
    if message.chat.id == message.from_user.id:
        await message.answer(f'{message.from_user.full_name},  за работу!',
                             reply_markup=inline_kb_menu.admin)


@dp.callback_query_handler(text='back_to_admin')
async def back_to_admin(call: CallbackQuery):
    text = f'Здравствуйте, {call.from_user.full_name},  вы попали в админ панель!'
    markup = inline_kb_menu.admin

    try:
        await call.message.edit_text(text=text, reply_markup=markup)
    except:
        await call.message.answer(text=text, reply_markup=markup)
