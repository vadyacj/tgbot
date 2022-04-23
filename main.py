from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import sqlite3
import random as rand
import config
import database
from database import BotDB


API_TOKEN = config.API_TOKEN
ADMIN = config.ADMIN

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылка"))
kb.add(types.InlineKeyboardButton(text="Статистика"))

us = types.ReplyKeyboardMarkup(resize_keyboard=True)
us.add(types.InlineKeyboardButton(text="100 на орла"))
us.add(types.InlineKeyboardButton(text="100 на решку"))
us.add(types.InlineKeyboardButton(text="Топ 10"))

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('db.db')
cur = conn.cursor()
conn.commit()
BotDB = BotDB('db.db')


class dialog(StatesGroup):
    spam = State()
    nameget = State()
    top10 = State()
    heads = State()
    tails = State()


@dp.message_handler(state=dialog.nameget)
async def getname(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    data = await state.get_data()
    name = data['username']
    result = "".join(name)
    try:
        BotDB.add_user(message.from_user.id, result)
    except sqlite3.IntegrityError:
        await message.answer('Имя занято, давай еще')
    else:
        await message.answer('Имя записано', reply_markup=us)
        await state.finish()


@dp.message_handler(commands=['start'])
async def start(message: Message):
    #BotDB.add_user(message.from_user.id)
    cur = conn.cursor()
    cur.execute(f'''SELECT status FROM users WHERE (user_id="{message.chat.id}")''')
    result = cur.fetchone()
    print(result, message.from_user.id)
    if message.from_user.id == ADMIN:                           #если админ
        await message.answer('Добро пожаловать в Админ-Панель! Выберите действие на клавиатуре', reply_markup=kb)
    else:
        if result is None:                                      #если пользователь впервые здесь здесь
            await message.answer('Введите ваше имя')
            await dialog.nameget.set()
        else:
            cur = conn.cursor()
            cur.execute(f"SELECT name FROM users WHERE user_id = {message.chat.id}")
            nameone = cur.fetchone()
            i = ''.join(map(str, nameone))
            await message.answer(f'Добро пожаловать, {i}!\nВыберите действие на клавиатуре', reply_markup=us)


@dp.message_handler(content_types=['text'], text='Топ 10')
async def topTen(message: Message, state: FSMContext):
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM users''')
    result = cur.fetchall()
    result.sort(key=lambda x: x[2], reverse=True)
    volume = len(result)
    if volume < 9:
        for x in range(volume):
            i = ' - '.join(map(str, result[x][2:4]))
            await message.answer(i)
    else:
        for x in range(10):
            i = ' - '.join(map(str, result[x][2:4]))
            await message.answer(i)
    cur.execute(f'''SELECT coins FROM users WHERE user_id = {message.chat.id}''')
    result = cur.fetchone()
    i = ''.join(map(str, result))
    await message.answer(f'У вас сейчас {i}',reply_markup=us)
    await state.finish()


@dp.message_handler(content_types=['text'], text='100 на орла')
@dp.message_handler(content_types=['text'], text='100 на решку')
async def startHeads(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Главное меню', reply_markup=us)
        await state.finish()
    else:
        num = rand.randrange(2)
        cur = conn.cursor()
        cur.execute(f"SELECT coins FROM users WHERE user_id = {message.chat.id}")
        ourwin = sum(cur.fetchone())
        if num == 1:
            ourwin = ourwin + 100
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET coins = {ourwin} WHERE user_id = {message.chat.id}")
            conn.commit()
            await message.answer(f'Вы выиграли', reply_markup=us)
            await state.finish()
        else:
            ourwin = ourwin - 100
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET coins = {ourwin} WHERE user_id = {message.chat.id}")
            conn.commit()
            await message.answer('Проигрыш',reply_markup=us)
            await state.finish()







@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: Message):
    await dialog.spam.set()
    await message.answer('Напиши текст рассылки')


@dp.message_handler(state=dialog.spam)
async def start_spam(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Главное меню', reply_markup=kb)
        await state.finish()
    else:
        cur = conn.cursor()
        cur.execute(f'''SELECT user_id FROM users''')
        spam_base = cur.fetchall()
        for z in range(len(spam_base)):
            await bot.send_message(spam_base[z][0], message.text)
            await message.answer('Рассылка завершена', reply_markup=kb)
            await state.finish()


@dp.message_handler(content_types=['text'], text='Статистика')
async def hfandler(message: types.Message, state: FSMContext):
    cur = conn.cursor()
    cur.execute('''select * from users''')
    results = cur.fetchall()
    await message.answer(f'Людей которые когда либо заходили в бота: {len(results)}')


if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)