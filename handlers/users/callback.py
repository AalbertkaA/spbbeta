from aiogram import types
from keyboards.inline import inline_kb_menu
from loader import dp, bot
from states.state import Registration_onTour
from utils.db_api.db_asyncpg import *
from aiogram.dispatcher import FSMContext


async def try_delete_call(call: types.CallbackQuery):
    try:
        await call.message.delete()
    except:
        pass


async def edit_call(callback, text, markup):
    try:
        msg = await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=markup)
    except:
        try:
            await callback.message.delete()
        except:
            pass
        msg = await callback.message.answer(text=text, parse_mode='HTML', reply_markup=markup)
    return msg


@dp.callback_query_handler(lambda query: query.data.startswith('active'))
async def spisok_tours(callback: types.CallbackQuery):
    tour_status = callback.data.split("/")[0]
    tour_date = callback.data.split("/")[1]

    tours_markup = await tours_in_date(tour_date)
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Выберите тур:",
        reply_markup=tours_markup
    )


@dp.callback_query_handler(text_startswith=('back_'))
async def go_back(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if callback.data == 'back_to_date':
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, text='Выберите дату тура', reply_markup=await active_tour_list())
    else:
        date = callback.data.split('_')[3]
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, text='Выберите тур:', reply_markup=await tours_in_date(date))


@dp.callback_query_handler(text_startswith=('bck_'))
async def go_bck(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    executor_id = int(callback.data.split("/")[1])
    desc, markup = await show_my_tours(executor_id)
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, text=desc, reply_markup=markup)


@dp.callback_query_handler(text_startswith=('bk_'))
async def go_bk(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    tour_id = int(callback.data.split("/")[1])
    result = await tour_inf(tour_id)

    previous_text = f"Название тура: {result['name']}\n" \
                    f"Дата: {result['date']}\n" \
                    f"Максимальное кол-во людей: {result['count_max']}"

    if result['status'] != 'active':
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=previous_text,
                                    reply_markup=inline_kb_menu.after_lock_tour(tour_id))
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=previous_text,
                                    reply_markup=inline_kb_menu.show_tour_adminchat(tour_id))


@dp.callback_query_handler(lambda query: query.data.startswith('tour'))
async def tours(callback: types.CallbackQuery):
    tour_id = int(callback.data.split("/")[1])
    string, tour_markup, tour_max = await tour_info(tour_id)
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=string,
        reply_markup=tour_markup
    )


@dp.callback_query_handler(lambda query: query.data.startswith('mtour'))
async def my_tours(callback: types.CallbackQuery):
    tour_id = int(callback.data.split("/")[1])
    executor_id = int(callback.data.split("/")[2])
    string, tour_markup = await my_tour_clients(tour_id, executor_id)
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=string,
        reply_markup=tour_markup
    )


@dp.callback_query_handler(lambda query: query.data.startswith('delete'))
async def delete_from_my_tours(callback: types.CallbackQuery):
    app_id = int(callback.data.split("/")[1])
    executor_id = int(callback.data.split("/")[2])
    tour_id = await delete_client_in_my_tour(app_id)
    current_keyboard = callback.message.reply_markup
    updated_keyboard = InlineKeyboardMarkup()

    # Обновляем inline клавиатуру, убирая удаленного клиента
    for button in current_keyboard.inline_keyboard:
        if button[0].callback_data != f'delete_client/{app_id}':
            updated_keyboard.row(button[0])

    # Обновляем описание тура с актуальным списком клиентов
    string, tour_markup = await my_tour_clients(tour_id, executor_id)
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=string,
        reply_markup=tour_markup
    )

    await callback.message.answer("Клиент удален")


@dp.callback_query_handler(lambda query: query.data.startswith('count_'))
async def change_count(callback_query: types.CallbackQuery):
    action = callback_query.data.split('_')[1]
    count = int(callback_query.data.split('_')[2])
    tour_id = int(callback_query.data.split('_')[3])
    desc, markup, tour_max = await tour_info(tour_id, count)

    if action == '-':
        if count <= 1:
            count = 1
        else:
            count = count - 1

    elif action == '+':
        if count < tour_max:
            count += 1

    desc, markup, tour_max = await tour_info(tour_id, count)

    await edit_call(callback_query, desc, markup)


@dp.callback_query_handler(lambda query: query.data.startswith('kount_'))
async def change_count_admin(callback_query: types.CallbackQuery):
    action = callback_query.data.split('_')[1]
    app_id = int(callback_query.data.split('_')[2])
    tour_id = int(callback_query.data.split('/')[1])

    app_info = await application_info(app_id)
    tour = await tour_inf(tour_id)

    user_count = app_info["client_count"]
    total_count = await tour_client_total_count(tour_id)
    count_max = tour["count_max"]

    if action == '-':
        user_count = 0 if user_count <= 1 else user_count - 1

    elif action == '+':
        if total_count < count_max:
            user_count += 1

    await update_count(user_count, app_id)

    try:
        await list_clients(callback_query)
    except:
        pass


@dp.callback_query_handler(lambda query: query.data.startswith('apply'))
async def tours(callback: types.CallbackQuery, state: FSMContext):
    count = int(callback.data.split('_')[1])
    tour_id = int(callback.data.split('_')[2])

    async with state.proxy() as data:
        data['count'] = count
        data['tour_id'] = tour_id

    await callback.message.answer('В любой момент можно отменить бронирование, написав мне «отмена»')
    await Registration_onTour.bilet_number.set()
    await callback.message.answer("Введите номер билета :")


@dp.callback_query_handler(lambda query: query.data.startswith('lock_'))
async def lock_tour(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    tour_id = int(callback.data.split('/')[1])
    res = await tour_inf(tour_id)

    await lock_tour_in_db(int(tour_id))
    await callback.answer(text=f'{res["name"]} {res["date"]}\nТур закрыт', show_alert=True)
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=inline_kb_menu.after_lock_tour(tour_id))


@dp.callback_query_handler(lambda query: query.data.startswith('list_'))
async def list_clients(callback: types.CallbackQuery):
    tour_id = int(callback.data.split('/')[1])

    apps = await all_tour_clients(tour_id)
    tour = await tour_inf(tour_id)

    desc = f"Информация о туре:\nНазвание: {tour['name']}\nДата: {tour['date']}\n"
    cc = 0
    for app in apps:
        desc += f"\n{app['user_name']} - {app['client_count']}"
        cc += app['client_count']

    if len(apps) > 0:
        desc += f"\n\nВсего клиентов: {cc}\n"
    else:
        desc += f"\n\nКлиентов нет\n"

    markup = admin_edit(apps, tour_id)
    await edit_call(callback, desc, markup)
