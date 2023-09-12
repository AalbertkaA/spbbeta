from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


admin = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [InlineKeyboardButton(text='Создать тур', callback_data=f'createTour')
         ],
        [InlineKeyboardButton(text='Статистика', callback_data=f'editTour')
         ]
    ]
)


def show_tour_adminchat(tour_id):
    btns = list()
    btns.append([InlineKeyboardButton("Закрыть тур", callback_data=f"lock_/{tour_id}")])
    btns.append([InlineKeyboardButton("Список клиентов", callback_data=f"list_clients/{tour_id}")])
    return InlineKeyboardMarkup(inline_keyboard=btns, row_width=1)


def after_lock_tour(tour_id):
    btns = list()
    btns.append([InlineKeyboardButton("Список клиентов", callback_data=f"list_clients/{tour_id}")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def admin_edit(executor, tour_id):
    btns = list()
    for user in executor:
        btns.append([InlineKeyboardButton(text=f'{user["user_name"]}', callback_data=f'_'),
                     InlineKeyboardButton(text='➖', callback_data=f'kount_-_{user["app_id"]}_/{tour_id}'),
                     InlineKeyboardButton(text=f'{user["client_count"]}', callback_data=f'_'),
                     InlineKeyboardButton(text='➕', callback_data=f'kount_+_{user["app_id"]}_/{tour_id}')])
    btns.append([InlineKeyboardButton(text='Назад', callback_data=f'bk_/{tour_id}')])
    return InlineKeyboardMarkup(inline_keyboard=btns)
