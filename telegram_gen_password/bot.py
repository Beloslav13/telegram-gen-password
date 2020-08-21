import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from char_collection.collect_password import CollectPassword

from telegram_gen_password._data import TOKEN
logging.basicConfig(level=logging.INFO)

API_TOKEN = TOKEN


bot = Bot(token=API_TOKEN)
generator = CollectPassword()

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    start = State()  # Will be represented in storage as 'Form:name'
    len_password = State()  # Will be represented in storage as 'Form:age'
    end = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.start.set()

    first_name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Сгенерировать пароль', 'Не, спасибо')
    tmp = f'Привет, {first_name}!\nЯ могу сгенерировать тебе пароль от 6 до 20 символов включая специальные символы!\n' \
          f'В любой момент можешь отправить /q или просто q для выхода.'
    await message.reply(tmp, reply_markup=markup)


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='q')
@dp.message_handler(Text(equals='q', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Отмена операций.\nДля запуска снова наберите /start', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.start)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['start'] = message.text.lower()
    if data['start'] == 'сгенерировать пароль':
        markup = types.ReplyKeyboardRemove()
        await message.answer('Какой длинны?', reply_markup=markup)
        await Form.next()
    elif data['start'] == 'не, спасибо':
        markup = types.ReplyKeyboardRemove()
        await message.answer('Ок, давай.\nДля запуска снова наберите /start', reply_markup=markup)
        await state.finish()

    else:
        await message.reply('Тут два варианта:\n'
                            'Левая кнопка - генерирую пароль.\n'
                            'Правая кнопка - выход.')


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.len_password)
async def process_age_invalid(message: types.Message):
    """
    If password is invalid
    """
    return await message.reply("Длинна пароля - это цифры!\nПопробуй ещё раз.")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.len_password)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['len_password'] = int(message.text)
    print(data['len_password'])

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Ещё раз', 'Подойдёт')
    result = generator(data['len_password'])
    if result is None:
        result = 'Пароль должен быть от 6 до 20 символов!'
        await message.reply(result, reply_markup=None)
    else:
        await Form.next()
        await message.reply(result, reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ['Ещё раз', 'Подойдёт'], state=Form.end)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    await Form.start.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Сгенерировать пароль', 'Не, спасибо')
    return await message.reply('И тебе спасибо.', reply_markup=markup)


@dp.message_handler(state=Form.end)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['end'] = message.text

    if data['end'] == 'Подойдёт':
        markup = types.ReplyKeyboardRemove()
        await message.answer('Ок, давай.\nДля запуска снова наберите /start', reply_markup=markup)
        await state.finish()
    elif data['end'] == 'Ещё раз':
        markup = types.ReplyKeyboardRemove()
        await message.answer('Какой длинны?', reply_markup=markup)
        await Form.len_password.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
