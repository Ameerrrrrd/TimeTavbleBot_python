import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from kbb import keyboard_reply as kb_reply
from aiogram.filters import CommandStart
from datetime import datetime, timedelta
import requests

bot = Bot('8192247154:AAE2mFLGN__f9kA3IQYyJayZZEzodje_1i8')
dp = Dispatcher()
url_getGroup = 'https://mgke.keller.by/api/getGroups'
url_getSchedule = 'https://mgke.keller.by/api/getGroup'
headers_auth = {'Authorization': 'Bearer 5_Dl6NZz3ZUuh0tIFtLpQtx9E-5XY6pjZMytxeUCqzCXkbt4TTl4B5-1FQNEA0s1S8XmKg'}

response = requests.get(url_getGroup, headers=headers_auth)


class ScheduleStates(StatesGroup):
    schedule_data = State()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply('Привет!')
    await message.answer('Выбери номер группы')


@dp.message(lambda message: len(message.text) <= 3)
async def get_group(message: Message, state: FSMContext):
    if response.status_code == 200:

        response_data = response.json().get('response', [])
        if response_data:
            user_input_group = message.text
            user_input_group_int = int(user_input_group)
            try:
                if user_input_group_int in response_data:
                    process = await message.answer("Обработка...")
                    await asyncio.sleep(0.5)
                    await bot.delete_message(chat_id=message.chat.id, message_id=process.message_id)

                    await get_schedule(message)
                    payload = {"group": user_input_group_int}
                    schedule = requests.post(url_getSchedule, json=payload, headers=headers_auth)
                    response_schedule = schedule.json()

                    await state.update_data(schedule=response_schedule)

                else:
                    await message.answer("Такой группы нет.")
            except ValueError:
                await message.answer("Введите корректное число.")
        else:
            await message.answer("Ошибка: данные не получены или список пуст.")
    else:
        await message.answer(f"Ошибка при запросе данных: {response.status_code}, {response.text}")


async def get_schedule(message: Message):
    try:
        await message.answer("Выбери нужное: ", reply_markup=kb_reply)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")


@dp.message(F.text.lower() == 'расписание на день')
async def show_schedule_day_reply(message: Message, state: FSMContext):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%d.%m.%Y")

    user_data = await state.get_data()
    schedule = user_data.get('schedule')

    if not schedule:
        await message.answer("Расписание не найдено.")
        return

    tomorrow_schedule = None
    for day_data in schedule['response']['days']:
        if day_data['day'] == tomorrow_str:
            tomorrow_schedule = day_data['lessons']
            break
    lesson_number = 1
    if tomorrow_schedule:
        schedule_text = f"<b>Расписание на {tomorrow_str}:</b>\n"
        for lesson in tomorrow_schedule:
            if lesson is None:
                lesson_number += 1
                continue
            else:
                schedule_text += f"<b>{str(lesson_number)}. </b>"
                if isinstance(lesson, list):
                    for subgroup in lesson:
                        schedule_text += (f"\n{subgroup['subgroup']}: "
                                          f"<b>{subgroup['lesson']} ({subgroup['type']}),</b> "
                                          f"{subgroup['teacher']}, "
                                          f"\n<i>Кабинет:</i> <b>{subgroup.get('cabinet', 'не указано')}</b>")
                else:
                    schedule_text += (f"<b> {lesson['lesson']} ({lesson['type']}),</b> "
                                      f"{lesson['teacher']}, "
                                      f"\n<i>Кабинет:</i> <b>{lesson.get('cabinet', 'не указано')}</b>")
                lesson_number += 1
                schedule_text += '\n<b>-------------------------------</b>\n'

        await message.answer(schedule_text, parse_mode="HTML")
    else:
        await message.answer(f"Расписание на {tomorrow_str} не найдено.")


@dp.message(F.text.lower() == 'расписание на неделю')
async def show_schedule_week(message: Message, state: FSMContext):

    user_data = await state.get_data()
    schedule = user_data.get('schedule')

    if not schedule:
        await message.answer("Расписание не найдено.")
        return

    days = schedule['response']['days']
    schedule_text = ""

    for day_data in days:
        day_str = day_data['day']
        weekday = day_data['weekday']
        lessons = day_data['lessons']
        lesson_number = 1
        schedule_text += f"\n📅 <b>{weekday}, {day_str}:</b>\n"

        for lesson in lessons:
            if lesson is None:
                lesson_number += 1
                continue
            schedule_text += f"<b>{str(lesson_number)}. </b>"
            if isinstance(lesson, list):
                for subgroup in lesson:
                    schedule_text += (f"\n{subgroup['subgroup']}: "
                                      f"<b>{subgroup['lesson']} ({subgroup['type']}),</b> "
                                      f"{subgroup['teacher']}, "
                                      f"\n<i>Кабинет:</i> <b>{subgroup.get('cabinet', 'не указано')}</b>")
            else:
                schedule_text += (f"<b> {lesson['lesson']} ({lesson['type']}),</b> "
                                  f"{lesson['teacher']}, "
                                  f"\n<i>Кабинет:</i> <b>{lesson.get('cabinet', 'не указано')}</b>")
            lesson_number += 1
            schedule_text += '\n<b>-------------------------------</b>\n'
        schedule_text += '\n\n'

    if schedule_text:
        await message.answer(schedule_text, parse_mode="HTML")
    else:
        await message.answer("Расписание пустое или не найдено.")


@dp.message(lambda message: message.text.lower() == 'сменить группу')
async def change_group(message: Message):
    await message.reply('Выбери группу: ')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
