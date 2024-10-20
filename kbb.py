from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

keyboard_reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Расписание на день'),
     KeyboardButton(text='Расписание на неделю')],
    [KeyboardButton(text='Сменить группу')],
    [KeyboardButton(text='Анекдот')]
    ],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите пункт меню...'
)