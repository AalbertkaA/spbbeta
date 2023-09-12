from handlers.users.start import command_start
from loader import dp
from aiogram.dispatcher.filters import Text
from keyboards.default import keyboard_menu
from aiogram.types import CallbackQuery, InputFile
from keyboards.inline.inline_kb_menu import *
from keyboards.default.keyboard_menu import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.db_api.db_asyncpg import *
from states.state import *
from utils.db_api.db_asyncpg import add_user_bd
from aiogram.utils.markdown import hlink


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contacts(message: types.Message):
    if message.contact.user_id != message.from_user.id:
        await message.answer('Поделитесь номером телефона, нажав кнопку ниже: «Отправить номер телефона»',
                             reply_markup=keyboard_menu.phone)
    else:
        user_id = int(message.from_user.id)
        user_full_name = message.from_user.full_name
        number = message.contact.phone_number
        await user_exists(message.from_user.id)
        await add_user_bd(user_id, user_full_name, number)
        await command_start(message)


@dp.message_handler(Text(equals="Активные туры"))
async def new_tours(message: types.Message):
    markup = await active_tour_list()
    if markup:
        await message.answer(text="Выберите дату", reply_markup=markup)
    else:
        await message.answer(text="Активных туров пока нет")


@dp.message_handler(Text(equals="Мои туры"))
async def my_tours(message: types.Message):
    executor_id = int(message.from_user.id)
    string, markup = await show_my_tours(executor_id)
    if markup:
        await message.answer(text=string, reply_markup=markup)
    else:
        await message.answer(text=string)


@dp.message_handler(Text(equals="Тех. поддержка"))
async def tech_help(message: types.Message):
    await message.answer(hlink('Напишите мне о проблеме, с которой вы столкнулись', 't.me/kkapysta'))


@dp.message_handler(lambda message: not message.text.isdigit(), state=Registration_onTour.bilet_number)
async def check_phone(message: types.Message):
    await message.reply('Напишите цифрами\n')


@dp.message_handler(state=Registration_onTour.bilet_number)
async def process_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer('Создание тура отменено', reply_markup=keyboard_menu.admin)
        await message.delete()
    else:
        async with state.proxy() as data:
            data['bilet_number'] = message.text
            check = await check_bilet_number(int(data['bilet_number']))
            if check:
                await message.answer("Такой номер билета уже зарегистрирован ранее. Введите другой номер")
                data['bilet_number'] = message.text

            else:
                count = data['count']
                tour_id = data['tour_id']

                await add_application_db(tour_id, int(data['bilet_number']), count, message.from_user.id)
                await message.answer("Спасибо! Данные успешно записаны ✅")
    await state.finish()


@dp.message_handler()
async def random_msg(message: types.Message) -> None:
    await command_start(message)

