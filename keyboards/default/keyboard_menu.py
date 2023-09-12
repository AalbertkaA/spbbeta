from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отправить номер телефона', request_contact=True),
        ]
    ],
    resize_keyboard=True
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Активные туры'),
        ],
        [
            KeyboardButton(text='Мои туры'),
        ],
        [
            KeyboardButton(text='Тех. поддержка'),
        ],
    ],
    resize_keyboard=True
)

admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='/admin'),
        ],

    ],
    resize_keyboard=True
)