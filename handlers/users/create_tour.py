from data.config import chatAdminTours
from filters import IsAdmin
from aiogram import types
from aiogram.types import CallbackQuery, InputFile
from loader import dp, bot
from aiogram.dispatcher.filters import Text
from keyboards.default import keyboard_menu
from keyboards.inline import inline_kb_menu
from states.state import Tour_Registration_byAdmin
from aiogram.dispatcher import FSMContext
from utils.db_api.db_asyncpg import *
from datetime import datetime, timedelta
from handlers.users.callback import try_delete_call


@dp.callback_query_handler(text='createTour')
async def createTour(call: CallbackQuery):
    await try_delete_call(call=call)
    await call.message.answer('В любой момент можно отменить создание тура, написав мне «отмена»')

    await Tour_Registration_byAdmin.tour_date.set()
    await call.message.answer('Для начала, введите дату. Введите дату в формате ГГГГ-ММ-ДД ЧЧ:ММ')


@dp.message_handler(state=Tour_Registration_byAdmin.tour_date)
async def process_description(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer('Создание тура отменено', reply_markup=keyboard_menu.admin)
        await state.finish()
    else:
        try:
            date = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
            async with state.proxy() as data:
                data['tour_date'] = date
            await Tour_Registration_byAdmin.next()
            await message.answer("Укажите название тура")
        except ValueError:
            await message.reply('Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД ЧЧ:ММ')


@dp.message_handler(state=Tour_Registration_byAdmin.title)
async def process_descriptio(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer('Создание тура отменено', reply_markup=keyboard_menu.admin)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['title'] = message.text
        await Tour_Registration_byAdmin.next()
        await message.answer("Укажите максимальное кол-во людей")


@dp.message_handler(lambda message: not message.text.isdigit(),
                    state=Tour_Registration_byAdmin.count_max)
async def check_number(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer('Создание тура отменено', reply_markup=keyboard_menu.admin)
        await state.finish()
    else:
        await message.reply('Напишите цифрой\n')


@dp.message_handler(state=Tour_Registration_byAdmin.count_max)
async def process_descripti(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count_max'] = int(message.text)

    await state.finish()
    tour_id = await add_tour_bd(data['title'], int(data['count_max']), data["tour_date"])

    message_text = f"Название тура: {data['title']}\n" \
                   f"Дата: {data['tour_date']}\n" \
                   f"Максимальное кол-во людей: {data['count_max']}"

    await bot.send_message(chatAdminTours, message_text,
                           reply_markup=inline_kb_menu.show_tour_adminchat(tour_id))
    await message.answer("Спасибо! Данные о туре записаны ✅")
    return message_text
