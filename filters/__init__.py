from .isadmin import IsAdmin

from aiogram import Dispatcher


def setup (dp: Dispatcher):
    dp.filters_factory.bind(IsAdmin)