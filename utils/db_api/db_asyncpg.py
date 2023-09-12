from datetime import datetime

from keyboards.inline import *
from loader import dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def user_exists(user_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow('SELECT * FROM "users" WHERE "user_id"=$1', user_id)
            return result is not None


async def add_user_bd(user_id: int, user_full_name, user_phone):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                'INSERT INTO users ("user_id", "user_name", "user_phone") VALUES ($1, $2, $3) ON CONFLICT (user_id) '
                'DO NOTHING',
                int(user_id), user_full_name, user_phone)


async def status():
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            return await connection.fetch('SELECT "user_id" FROM "users" WHERE "user_status"=$1', 'admin')


async def active_tour_list():
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            results = await connection.fetch(
                'SELECT DISTINCT ON (tour_date) * FROM "tours" WHERE tour_status = $1', 'active')
            # print(results)
            if results:
                markup = InlineKeyboardMarkup(row_width=1)
                btns = []
                for row in results:
                    date = row[2]
                    tour_status = row[3]
                    btns.append(InlineKeyboardButton(text=f'{date.strftime("%Y-%m-%d")}', callback_data=f'{tour_status}/{date}'))

                markup.add(*btns)
                return markup
            else:
                return None


async def tours_in_date(date):  # Выводит туры в кнопки по дате
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            results = await connection.fetch(
                'SELECT * FROM "tours" WHERE tour_status=$1 ORDER BY tour_date',
                'active')
            # print(results)

            markup = InlineKeyboardMarkup(row_width=1)
            btns = [InlineKeyboardButton(text=f'{i[1]}', callback_data=f'tour/{i[0]}') for i in results]
            markup.add(*btns, InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_date'))
            return markup


async def tour_inf(tour_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                'SELECT * FROM "tours" WHERE tour_id=$1', int(tour_id))
            # print(result)
            return result


async def tour_info(tour_id: int, count=1):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                'SELECT * FROM "tours" WHERE tour_id=$1', int(tour_id))
            tour_date = result['tour_date']
            if result:
                markup2 = InlineKeyboardMarkup()
                btns = [InlineKeyboardButton(text='➖', callback_data=f'count_-_{count}_{tour_id}'),
                        InlineKeyboardButton(text=f'{count}', callback_data=f'_'),
                        InlineKeyboardButton(text='➕', callback_data=f'count_+_{count}_{tour_id}')]
                markup2.add(*btns)
                count_app = await check_tour_count(tour_id)

                if result['tour_max'] - count_app > 0:
                    tour_max = result['tour_max'] - count_app
                    markup2.add(InlineKeyboardButton(text='Забронировать', callback_data=f'apply_{count}_{tour_id}'))
                    markup2.add(InlineKeyboardButton(text='Назад', callback_data=f'back_to_title_{tour_date}'))
                else:
                    tour_max = 0
                    markup2.add(InlineKeyboardButton(text='Назад', callback_data=f'back_to_title_{tour_date}'))

                string = f"{result['tour_name']}\nДата: {result['tour_date']}\n\n" \
                         f"Свободных мест: {tour_max} "
                # print(string)
                return string, markup2, tour_max
            else:
                string = "Информация о туре не найдена."
                return string, None, None


async def add_tour_bd(tour_name, tour_max: int, tour_date):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                'INSERT INTO tours ("tour_name", "tour_max", "tour_date") '
                'VALUES ($1, $2, $3) RETURNING tour_id',
                tour_name, int(tour_max), tour_date)
            if result:
                tour_id = result['tour_id']
                return tour_id


async def add_application_db(tour_id, bilet_number, client_count, executor, executor_id):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            existing_record = await connection.fetchrow(
                'SELECT * FROM applications_beta1 WHERE tour_id = $1 AND executor_id = $2',
                tour_id, executor_id
            )

            if existing_record:
                await connection.execute(
                    'UPDATE applications_beta1 SET client_count = $1 WHERE tour_id = $2 AND executor_id = $3',
                    existing_record['client_count'] + client_count, tour_id, executor_id
                )
            else:
                await connection.execute(
                    'INSERT INTO applications_beta1 ("tour_id", "bilet_number", "client_count", "executor", "executor_id") '
                    'VALUES ($1, $2, $3, $4, $5)',
                    tour_id, bilet_number, client_count, executor, executor_id
                )


async def check_tour_count(tour_id: int):  # кол-во заявок по туру
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow("SELECT SUM(client_count) AS sum FROM applications_beta1"
                                               " WHERE tour_id = $1", tour_id)
            if result and result['sum'] is not None:
                count_app = int(result['sum'])
                return count_app
            else:
                return 0


async def show_my_tours(executor_id: int):  # Туры сотрудников
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            results = await connection.fetch(
                'SELECT * FROM "applications_beta1" WHERE executor_id=$1', executor_id)

            added_tours = set()
            markup7 = InlineKeyboardMarkup()

            for application in results:
                tour_id = application['tour_id']
                if tour_id not in added_tours:
                    added_tours.add(tour_id)
                    tour = await connection.fetchrow('SELECT * FROM "tours" WHERE tour_id=$1 AND tour_status=$2',
                                                     tour_id, 'active')
                    if tour:
                        tour_name = tour['tour_name']
                        tour_date = tour['tour_date'].strftime('%Y-%m-%d')
                        btn = InlineKeyboardButton(text=f'{tour_name} | {tour_date}',
                                                   callback_data=f'mtour_id/{tour_id}'
                                                                 f'/{executor_id}')
                        markup7.add(btn)

            if markup7.inline_keyboard:
                desc = "Ваши туры: "
                return desc, markup7
            else:
                desc = "У вас пока нет заявок на туры."
                return desc, None


async def all_tour_clients(tour_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            apps = await connection.fetch(
                'SELECT * FROM "applications_beta1" WHERE tour_id=$1 ORDER BY app_id', tour_id)
            return apps


async def tour_clients(tour_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            apps = await connection.fetch(
                'SELECT * FROM "applications_beta1" WHERE tour_id=$1', tour_id)
            print(apps)
            return apps


async def my_tour_clients(tour_id: int, executor_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            tour = await connection.fetchrow('SELECT * FROM "tours" WHERE tour_id=$1', tour_id)
            if not tour:
                desc = "Тур не найден"
                return desc, None

            tour_name = tour['tour_name']

            tour_date = tour['tour_date'].strftime('%Y-%m-%d')
            bilets = await connection.fetch(
                'SELECT * FROM "applications_beta1" WHERE tour_id=$1 AND executor_id=$2', tour_id, executor_id)
            print(bilets)

            if not bilets:
                desc = f"Информация о туре:\nНазвание: {tour_name}\nДата: {tour_date}\n\nУ " \
                       f"этого тура пока нет ваших клиентов. "

                return desc, None

            desc = f"Информация о туре:\n" \
                   f"Название: {tour_name}\n" \
                   f"Дата: {tour_date}\n\n" \
                   f"Билетов - {len(bilets)}:\n"

            markup = InlineKeyboardMarkup()
            for bilet in bilets:
                bilet_number = bilet['bilet_number']
                client_count = bilet['client_count']
                # btn = InlineKeyboardButton(text=f"удалить {client_name}", callback_data=f'delete_client/'
                # f'{client["app_id"]}/'
                # f'{executor_id}')
                # markup.add(btn)
                desc += f"№ {bilet_number}  Клиентов: {client_count}\n"

            markup.add(InlineKeyboardButton(text='Назад', callback_data=f'bck_/{executor_id}'))

            return desc, markup


async def delete_client_in_my_tour(app_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow("SELECT tour_id FROM applications_beta1 WHERE app_id = $1", app_id)
            if result:
                tour_id = result['tour_id']
                await connection.execute("DELETE FROM applications_beta1 WHERE app_id = $1", app_id)
                return tour_id
            else:
                return None


async def lock_tour_in_db(tour_id: int):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            await connection.execute("UPDATE tours SET tour_status = 'lock' WHERE tour_id = $1", tour_id)


async def check_bilet_number(bilet_number):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchval("SELECT EXISTS (SELECT 1 FROM applications_beta1"
                                               " WHERE bilet_number = $1)"
                                               , bilet_number)
            return bool(result)


async def update_count(count, app_id):
    async with dp['db_pool'].acquire() as connection:
        async with connection.transaction():
            await connection.execute('UPDATE applications_beta1 SET client_count = $1 WHERE app_id = $2',
                                     count, app_id)
