from utils.set_bot_commands import *
from handlers import dp
import asyncpg
from aiogram import executor


async def on_startup(dp):
    dp['db_pool'] = await create_db_pool()
    await set_default_commands(dp)


async def create_db_pool():
    return await asyncpg.create_pool(
        user='mars',
        password='AlbertKa',
        host='31.129.96.250',
        database='spbtours',
        max_size=100
    )


async def close_db_pool(pool):
    await pool.close()


async def on_shutdown(dp):
    # Закрытие пула подключений
    await dp['db_pool'].close()
    # Ожидание завершения всех активных соединений в пуле
    await dp['db_pool'].wait_closed()
    # Вывод сообщения о закрытии пула
    print("Пул подключений успешно закрыт")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup,
                           on_shutdown=on_shutdown)