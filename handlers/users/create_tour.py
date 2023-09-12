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


@dp.message_handler(Text(equals='отмена'), state="*")
async def command_cancel(message: types.Message, state: FSMContext) -> None:
    if state is None:
        return
    await state.finish()
    await message.answer('Создание тура отменено', reply_markup=keyboard_menu.admin)
    await message.delete()


@dp.callback_query_handler(text='createTour')
async def createTour(call: CallbackQuery):
    try:
        await call.message.delete()
    except:
        pass

    await call.message.answer('В любой момент можно отменить создание тура, написав мне «отмена»')

    await Tour_Registration_byAdmin.tour_date.set()
    await call.message.answer('Для начала, введите дату. Формат: год-месяц-день')


@dp.message_handler(lambda message: not message.text.isdigit(),
                    state=Tour_Registration_byAdmin.tour_date)
async def process_description(message: types.Message, state: FSMContext):
    date_format = '%Y-%m-%d %H:%M'
    try:

        async with state.proxy() as data:
            data['date'] = message.text
        await Tour_Registration_byAdmin.next()
        await message.answer("Укажите название тура")
    except ValueError:
        await message.reply('Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД ЧЧ:ММ')



@dp.message_handler(state=Tour_Registration_byAdmin.title)
async def process_descriptio(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await Tour_Registration_byAdmin.next()
    await message.answer("Укажите максимальное кол-во людей")


@dp.message_handler(lambda message: not message.text.isdigit(),
                    state=Tour_Registration_byAdmin.count_max)
async def check_number(message: types.Message):
    await message.reply('Напишите цифрой\n')


@dp.message_handler(state=Tour_Registration_byAdmin.count_max)
async def process_descripti(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count_max'] = message.text

    await state.finish()
    date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')

    tour_id = await add_tour_bd(data['title'], int(data['count_max']), date)
    tour_name = data['title']

    tour_date = date
    tour_max_count = data['count_max']

    message_text = f"Название тура: {data['title']}\n" \
                   f"Дата: {data['date']}\n" \
                   f"Максимальное кол-во людей: {data['count_max']}"

    await bot.send_message(chatAdminTours, message_text,
                           reply_markup=inline_kb_menu.show_tour_adminchat(tour_id))
    await message.answer("Спасибо! Данные о туре записаны ✅")
    return message_text
