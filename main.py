import requests
from aiogram import Bot, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import FiltersFactory
import config
from utils import States
from db import BotDB
from callbacks import *
import asyncio
from collectors import horoscope, currency

bot = Bot(token=config.REALISE_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
BotDB = BotDB()
filters = FiltersFactory(dp)

zodiac_signs = list(config.zodiac_signs_links.keys())


async def menu(message, text='Вы в меню'):
	state = dp.current_state(user=message.from_user.id)
	BotDB.update_status(message.from_user.id, "menu")
	btn1 = types.KeyboardButton(text="Гороскопы🪐")
	btn2 = types.KeyboardButton(text="Курсы валют💰")
	btn3 = types.KeyboardButton(text="Новости📰")
	btn5 = types.KeyboardButton(text="Инвестиции📈")
	btn4 = types.KeyboardButton(text="Настройки⚙")
	kb = [[btn1, btn2, btn3], [btn5, btn4]]
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
	await message.answer(text, reply_markup=markup)
	await state.set_state(States.MENU_STATE[0])


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
	state = dp.current_state(user=message.from_user.id)
	if (message.chat.id,) not in BotDB.get_id() or 1:
		await message.answer(
			f'{message.from_user.first_name}, здравствуйте, я новостной бот. Напишите мне день и месяц вашего рождения (через точку), чтобы получать гороскоп')
		if not BotDB.user_exists(message.chat.id):
			BotDB.add_user(
				message.chat.id, "welcome", f'{message.from_user.first_name}',
				message.from_user.username, "pass", '123')
		else:
			BotDB.update_status(message.chat.id, "welcome")

		await state.set_state(States.WELCOME_STATE[0])

	else:
		await message.answer("Я тебя помню")
		await menu(message, 'Вы в меню')


@dp.message_handler(state=States.WELCOME_STATE)
async def welcome(message: types.Message):
	state = dp.current_state(user=message.from_user.id)
	try:
		data = list(map(int, message.text.split(".")))
	except ValueError as e:
		await message.answer("Введены невенрные данные, попробуйте еще раз")
		return
	BotDB.add_birth(message.chat.id, message.text)
	if len(data) == 2 and 0 < data[0] < 32 and 0 < data[1] < 13:
		znak = "Овен"
		if (21 <= data[0] <= 31 and data[1] == 3) or (data[1] == 4 and 1 <= data[0] <= 19):
			znak = zodiac_signs[0]
		elif (20 <= data[0] <= 30 and data[1] == 4) or (data[1] == 5 and 1 <= data[0] <= 20):
			znak = zodiac_signs[1]
		elif (21 <= data[0] <= 31 and data[1] == 5) or (
				data[1] == 6 and 1 <= data[0] <= 21):
			znak = zodiac_signs[2]
		elif (22 <= data[0] <= 30 and data[1] == 6) or (
				data[1] == 7 and 1 <= data[0] <= 22):
			znak = zodiac_signs[3]
		elif (23 <= data[0] <= 31 and data[1] == 7) or (
				data[1] == 8 and 1 <= data[0] <= 22):
			znak = zodiac_signs[4]
		elif (23 <= data[0] <= 31 and data[1] == 8) or (
				data[1] == 9 and 1 <= data[0] <= 22):
			znak = zodiac_signs[5]
		elif (23 <= data[0] <= 30 and data[1] == 9) or (
				data[1] == 10 and 1 <= data[0] <= 23):
			znak = zodiac_signs[6]
		elif (24 <= data[0] <= 31 and data[1] == 10) or (
				data[1] == 11 and 1 <= data[0] <= 22):
			znak = zodiac_signs[7]
		elif (23 <= data[0] <= 30 and data[1] == 11) or (
				data[1] == 12 and 1 <= data[0] <= 21):
			znak = zodiac_signs[8]
		elif (22 <= data[0] <= 31 and data[1] == 12) or (
				data[1] == 1 and 1 <= data[0] <= 20):
			znak = zodiac_signs[9]
		elif (21 <= data[0] <= 31 and data[1] == 1) or (
				data[1] == 2 and 1 <= data[0] <= 18):
			znak = zodiac_signs[10]
		elif (19 <= data[0] <= 29 and data[1] == 2) or (
				data[1] == 3 and 1 <= data[0] <= 20):
			znak = zodiac_signs[11]

		await message.answer(f"А вы знали, что Вы {znak}?")
		BotDB.update_status(message.chat.id, "pass")
		BotDB.update_znak(message.chat.id, znak)
		await menu(
			message,
			"Теперь каждое утро в 8 часов вы будете получать актуальный гороскоп, новости и курс валют.")
		await state.set_state(States.MENU_STATE[0])
	else:
		await message.answer("Введены невенрные данные, попробуйте еще раз")


@dp.message_handler(state=States.MENU_STATE)
async def first_test_state_case_met(message: types.Message):
	state = dp.current_state(user=message.from_user.id)
	if message.text == 'Инвестиции📈':
		BotDB.update_status(message.chat.id, "invest")

	if message.text == "Гороскопы🪐":
		BotDB.update_status(message.chat.id, "horoscope")
		btn1 = types.KeyboardButton(text=zodiac_signs[0])
		btn2 = types.KeyboardButton(text=zodiac_signs[1])
		btn3 = types.KeyboardButton(text=zodiac_signs[2])
		btn4 = types.KeyboardButton(text=zodiac_signs[3])
		btn5 = types.KeyboardButton(text=zodiac_signs[4])
		btn6 = types.KeyboardButton(text=zodiac_signs[5])
		btn7 = types.KeyboardButton(text=zodiac_signs[6])
		btn8 = types.KeyboardButton(text=zodiac_signs[7])
		btn9 = types.KeyboardButton(text=zodiac_signs[8])
		btn10 = types.KeyboardButton(text=zodiac_signs[9])
		btn11 = types.KeyboardButton(text=zodiac_signs[10])
		btn12 = types.KeyboardButton(text=zodiac_signs[11])
		back = types.KeyboardButton(text="Меню↩")
		kb = [
			[btn1, btn2, btn3, btn4],
			[btn5, btn6, btn7, btn8],
			[btn9, btn10, btn11, btn12],
			[back]
		]
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
		await message.answer(
			"Выберите знак зодиака для которого хотите узнать гороскоп",
			reply_markup=markup)
		await state.set_state(States.CHOOSING_HOROSCOPE[0])

	if message.text == "Новости📰":
		BotDB.update_status(message.chat.id, "news")

		home = types.KeyboardButton(text="Меню↩")
		markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[home]])
		await message.answer("Чтобы вернуться, нажмите кнопку меню", reply_markup=markup1)
		btn_0 = types.InlineKeyboardButton(
			text='Глвное❗', callback_data="https://dzen.ru/news")
		btn_1 = types.InlineKeyboardButton(
			ext='Казань🕌', callback_data="https://dzen.ru/news/region/kazan")
		btn_2 = types.InlineKeyboardButton(
			text='Коронавирус🦠',
			callback_data="https://dzen.ru/news/rubric/koronavirus")
		btn_3 = types.InlineKeyboardButton(
			text='Политика🇺🇳', callback_data="https://dzen.ru/news/rubric/politics")
		btn_4 = types.InlineKeyboardButton(
			text='Экономика📈', callback_data="https://dzen.ru/news/rubric/business")
		btn_5 = types.InlineKeyboardButton(
			text='Спорт⚽️',
			callback_data="https://dzen.ru/sport?utm_source=yxnews&utm_medium=desktop")
		btn_6 = types.InlineKeyboardButton(
			text='Происшествия🚨',
			callback_data="https://dzen.ru/news/rubric/incident")
		btn_7 = types.InlineKeyboardButton(
			text='Культура🎨', callback_data="https://dzen.ru/news/rubric/culture")
		btn_8 = types.InlineKeyboardButton(
			text='Технологии💻', callback_data="https://dzen.ru/news/rubric/computers")
		kb = [
			[btn_0],
			[btn_1],
			[btn_2],
			[btn_3],
			[btn_4],
			[btn_5],
			[btn_6],
			[btn_7],
			[btn_8]
		]
		markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
		await message.answer("Выберите тему", reply_markup=markup)
		await state.set_state(States.CHOOSING_CATEGORIES_NEWS[0])

	if message.text == "Курсы валют💰":
		BotDB.update_status(message.chat.id, "curr")
		curr = currency.get()
		btns = [[
			types.InlineKeyboardButton(
				text="Другая валюта",
				callback_data="other_currency")
		]]
		builder = InlineKeyboardMarkup(inline_keyboard=btns)
		await message.answer(
			f"{curr['USD']['name']} (USD): {curr['USD']['val']}₽\n"
			f"{curr['EUR']['name']} (EUR): {curr['EUR']['val']}₽",
			reply_markup=builder)
		await state.set_state(States.MENU_STATE[0])
	if message.text == "Настройки⚙":
		BotDB.update_status(message.chat.id, "settings")


@dp.message_handler(state=States.CHOOSING_HOROSCOPE)
async def choosing_horoscope(message: types.Message):
	if message.text == 'Меню↩':
		await menu(message)
	elif message.text in zodiac_signs:
		await message.answer(horoscope.get(config.zodiac_signs_links[message.text])[0])
		for i in horoscope.get(config.zodiac_signs_links[message.text])[1]:
			await message.answer(i.text)
	else:
		await message.answer("Я не понимаю")


@dp.callback_query_handler(text_contains='curr_')
async def send_random_value(callback: types.CallbackQuery):
	builder = InlineKeyboardMarkup()
	curr = currency.get()
	key = callback.data.split('_')[1]
	print(key)
	builder.add(types.InlineKeyboardButton(
		text="Другая валюта",
		callback_data="other_currency")
	)
	await callback.message.answer(
		f"{curr[key]['name']} ({key}): {curr[key]['val']}₽\n",
		reply_markup=builder)
	await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query_handler(text_contains='other_currency')
async def send_random_value(callback: types.CallbackQuery):
	curr = currency.get()
	keys = sorted(list(curr.keys()), key=lambda x: curr[x]['name'])
	btns = []
	for i in range(0, len(keys) - 1, 2):
		btns.append([
			types.InlineKeyboardButton(
				text=f"{curr[keys[i]]['name']} ({keys[i]})",
				callback_data=f"curr_{keys[i]}"),
			types.InlineKeyboardButton(
				text=f"{curr[keys[i + 1]]['name']} ({keys[i + 1]})",
				callback_data=f"curr_{keys[i + 1]}"),
		])
	builder = InlineKeyboardMarkup(inline_keyboard=btns)
	await callback.message.answer(
		"Выберите валюу:",
		reply_markup=builder)


@dp.callback_query_handler(state=States.CHOOSING_CATEGORIES_NEWS)
async def send_random_value(callback: types.CallbackQuery):
	print(callback.data)


@dp.message_handler(state="*")
async def all_cmd(message: types.Message):
	await menu(message)


# Запуск процесса поллинга новых апдейтов
async def main():
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())