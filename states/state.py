from aiogram.dispatcher.filters.state import StatesGroup, State


class Tour_Registration_byAdmin(StatesGroup):
    tour_date = State() #дата
    title = State() #имя
    count_max = State()  # количество максимальное
    decs = State() #описание


class Registration_onTour(StatesGroup):
    bilet_number = State() #имя


