"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging

from aiogram import Bot, Dispatcher, executor, types
from char_collection.collect_password import CollectPassword

from telegram_gen_password._data import TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
generator = CollectPassword()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    first_name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Сгенерировать пароль', 'Не, спасибо')
    tmp = f'Привет, {first_name}!\nЯ могу сгенерировать тебе пароль от 6 до 20 символов включая специальные символы!'
    await message.reply(tmp, reply_markup=markup)


@dp.message_handler(lambda message: message.text)
async def generate_password(message: types.Message):
    if message.text.lower() in ['сгенерировать пароль', 'ещё раз']:
        markup = types.ReplyKeyboardRemove()
        await message.answer('Какой длинны?', reply_markup=markup)
    # Генерируем пароль и отправляем пользователю
    elif message.text.isdigit():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Ещё раз', 'Подойдёт')
        message.text = int(message.text)
        result = generator(message.text)
        if result is None:
            result = 'Пароль должен быть от 6 до 20 символов!'
        await message.reply(result, reply_markup=markup)
    # Заканчиваем диалог с пользовальетелем
    elif message.text.lower() in ['не, спасибо', 'подойдёт']:
        markup = types.ReplyKeyboardRemove()
        await message.answer('Ок, давай.', reply_markup=markup)
    # Пользователь отправил что-то не понятное
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Сгенерировать пароль', 'Не, спасибо')
        await message.answer('Не, ты не понял? Я пароль только генерирую, больше ничего тебе не отвечу и не скажу.',
                             reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
