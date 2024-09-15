from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

# Клавиатура при подаче заявки на канал


keyboard_start_button = KeyboardButton('Я человек 🙋')

keyboard_start = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_start.add(keyboard_start_button)

# Кнопки после нажатия на "Я человек" | Обычный пользователь 

keyboard_main_button1 = KeyboardButton('Связь с админом 📞')
keyboard_main_button2 = KeyboardButton('Бросить кубик 🎲')

keyboard_main = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_main.add(keyboard_main_button1)
keyboard_main.add(keyboard_main_button2)

# Клавиатура для админа

keyboard_admin_button1 = KeyboardButton('Сделать рассылку 💬')
keyboard_admin_button2 = KeyboardButton('Статистика 📊')

keyboard_admin = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_admin.add(keyboard_admin_button1)
keyboard_admin.add(keyboard_admin_button2)

# Клавиатура для рассылки
keyboard_mailing = InlineKeyboardMarkup(row_width=2)
keyboard_mailing.add(
        InlineKeyboardButton("Подтвердить ✅", callback_data="confirm_mailing"),
        InlineKeyboardButton("Отменить ❌", callback_data="cancel_mailing")
)