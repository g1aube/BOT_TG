import os
import sys

sys.path.append(f'/Users/gorobtsov/Desktop/bot_tg/keyboard')
sys.path.append(f'/Users/gorobtsov/Desktop/bot_tg/settings')
sys.path.append(f'/Users/gorobtsov/Desktop/bot_tg/database')

from keyboard import keyboard_start, keyboard_main, keyboard_admin, keyboard_mailing
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from config import token, MAIN_ADMIN
from database import db


bot = Bot(token=token)

dp = Dispatcher(bot=bot, storage=MemoryStorage())


class FormState(StatesGroup):
    waiting_for_message = State()

class FormAdminMailing(StatesGroup):
    text = State()
    photo = State()
    confirmation = State()

# Принятие заявок людей
@dp.chat_join_request_handler()
async def start_message(update: types.ChatJoinRequest):
    # тут мы принимаем юзера в канал
    await update.approve()
    # а тут отправляем сообщение
    await bot.send_message(chat_id=update.from_user.id, text="""                           
<b>Привет, спасибо за подписку на канал!</b>

Я бот помощник канала про финансы и экономику 

Для подтверждения того, что вы живой человек, нажмите кнопку
<b>«Я человек»</b>
или напишите мне.""", parse_mode='HTML', reply_markup=keyboard_start)
    

# Человек просто написал сообщение в чат
@dp.message_handler()
async def message_from_user(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    db.check_user(telegram_id=user_id, username=username)
    check_user_id = db.check_user_id(telegram_id=user_id)[0][0]
    check_user = db.check_admin(telegram_id=check_user_id)
    if check_user == []:
        await message.answer("Рад снова тебя видеть", reply_markup=keyboard_main)
    else:
        await message.answer("Добро пожаловать, администратор!", reply_markup=keyboard_admin)


# Непосредственное нажатие на кнопку "Я человек"
@dp.message_handler(text='Я человек 🙋')
async def start_message_human(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    db.check_user(telegram_id=user_id, username=username)
    await bot.send_message(message.chat.id, text="""
<b>Ваша заявка одобрена модераторами!</b> 
""", parse_mode='HTML', reply_markup=keyboard_main)
    
# Нажатие на кнопку "Бросить кубик"
@dp.message_handler(text='Бросить кубик 🎲')
async def cubik(message: Message):
    await bot.send_dice(message.chat.id)

# Нажатие на кнопку "Связь с админом"
@dp.message_handler(text='Связь с админом 📞')
async def say_admin(message: Message):
    telegram_id = message.from_user.id
    check_user_id = db.check_user_id(telegram_id=telegram_id)[0][0]
    check_user = db.check_admin(telegram_id=check_user_id)
    if check_user == []:
        await FormState.waiting_for_message.set()
        await bot.send_message(message.chat.id, """                               
Напишите ваше сообщение администратору:
                               
Вы можете отправлять только текст, картинки и видеоформат не будут отправлены, бот их просто проигнорирует.
""")
    else:
        await bot.send_message(message.chat.id, "Вы не можете отправлять сообщение самому себе :)", reply_markup=keyboard_admin)

# Обработка сообщения от пользователя
@dp.message_handler(state=FormState.waiting_for_message, content_types=types.ContentTypes.TEXT)
async def process_message(message: types.Message, state: FSMContext):
    try:
        user_message = message.text
        await bot.send_message(MAIN_ADMIN, f"Сообщение от {message.from_user.full_name} (ID: {message.from_user.id} | username: @{message.from_user.username}):\n\n{user_message}")
        await message.answer("Ваше сообщение отправлено администратору.")
        await state.finish()
        
    except Exception as ex:
        await bot.send_message(message.from_user.id, "Что-то пошло не так, попробуйте снова", reply_markup=keyboard_main)
        await state.finish()

@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    telegram_id = message.from_user.id
    check_user_id = db.check_user_id(telegram_id=telegram_id)[0][0]
    check_user = db.check_admin(telegram_id=check_user_id)
    if check_user == []:
        await message.answer("Рад снова тебя видеть", reply_markup=keyboard_main)
    else:
        await message.answer("Добро пожаловать, администратор!", reply_markup=keyboard_admin)

# --- РАССЫЛКА ---
# Кнопка: сделать рассылку для админа
@dp.message_handler(text='Сделать рассылку 💬')
async def mailing(message: types.Message):
    telegram_id = message.from_user.id
    check_user_id = db.check_user_id(telegram_id=telegram_id)[0][0]
    check_user = db.check_admin(telegram_id=check_user_id)
    if check_user == []:
        await message.answer('Эта функция доступна только администратору!', reply_markup=keyboard_start)
    else:
        await FormAdminMailing.text.set()
        await message.answer("Введите текст для рассылки:")

@dp.message_handler(state=FormAdminMailing.text)
async def mailing_process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await FormAdminMailing.photo.set()
    await message.answer("Прикрепите фото (или отправьте 'нет', если не хотите прикреплять):")

@dp.message_handler(state=FormAdminMailing.photo, content_types=types.ContentTypes.PHOTO)
async def mailing_process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await send_confirmation(message.chat.id, data.get('text'), True, data)
    except Exception as ex:
        await FormAdminMailing.photo.set()
        await message.answer(f"""
Отправьте еще раз фотографию для рассылки
""")
        

@dp.message_handler(state=FormAdminMailing.photo, content_types=types.ContentTypes.TEXT)
async def mailing_process_no_photo(message: types.Message, state: FSMContext):
    if message.text.lower() == 'нет':
        data = await state.get_data()
        text = data.get('text')
        await send_confirmation(message.chat.id, text, False, data)
    else:
        await message.answer("Пожалуйста, прикрепите фото или отправьте 'нет'.")


async def send_confirmation(chat_id, text, has_photo, data):    
    if has_photo:
        await bot.send_photo(chat_id, photo=data.get('photo'), caption=text, reply_markup=keyboard_mailing)
        await FormAdminMailing.confirmation.set()
    else:
        await bot.send_message(chat_id, text=text, reply_markup=keyboard_mailing)
        await FormAdminMailing.confirmation.set()


@dp.callback_query_handler(text=['confirm_mailing', 'cancel_mailing'], state=FormAdminMailing.confirmation)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    photo = data.get('photo')

    if callback_query.data == 'confirm_mailing':
        users = db.get_all_users()
        for user_id in users:
            try:
                if photo:
                    await bot.send_photo(user_id[1], photo=photo, caption=text)  # Используем photo
                else:
                    await bot.send_message(user_id[1], text)
            except Exception as ex:
                continue
        
        await bot.send_message(callback_query.from_user.id, "Рассылка завершена!")
        await state.finish()
    
    else:
        await bot.send_message(callback_query.from_user.id, text='Рассылка отменена!', reply_markup=keyboard_admin)
        await state.finish()


# --- СТАТИСТИКА ---
# Нажатие админом на кнопку "Статистика"
@dp.message_handler(text='Статистика 📊')
async def statistics_command(message: types.Message):
    telegram_id = message.from_user.id
    check_user_id = db.check_user_id(telegram_id=telegram_id)[0][0]
    check_user = db.check_admin(telegram_id=check_user_id)
    if check_user == []:
        await message.answer('Эта функция доступна только администратору!', reply_markup=keyboard_start)
    else:
        all_users = len(db.get_all_users())
        all_admins = len(db.get_all_admins())

        await message.answer(f'''
СТАТИСТИКА БОТА:
Всего пользователей: {all_users}
Всего администраторов: {all_admins}                          
''')

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)