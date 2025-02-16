from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from object import category_list

def send_photo_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Отправить номер телефона 📱", request_contact=True)
    markup.add(button1)
    return markup

def back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = KeyboardButton("⬅️ Назад")

    markup.row(buttons)
    return markup

def catalog_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for i in category_list:
        buttons.append(KeyboardButton(f"{i}"))
    buttons.append(KeyboardButton("Корзина 🧺"))
    buttons.append(KeyboardButton("Мои заказы ✅"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup

def catalog_button_for_admin():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for i in category_list:
        buttons.append(KeyboardButton(f"{i}"))
    buttons.append(KeyboardButton("Корзина 🧺"))
    buttons.append(KeyboardButton("Добавить товар"))
    buttons.append(KeyboardButton("Изменить фото категории"))
    buttons.append(KeyboardButton("Отчет по продажам"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup


def add_product_for_admin():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for i in category_list:
        buttons.append(KeyboardButton(f"{i}"))
    buttons.append(KeyboardButton("⬅️ Назад"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup


# Продукты 1й котегории
def catalog1_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Фаланга краба Extra"),
        KeyboardButton("Cвежезамороженные креветки в панцире 500гр Размер 16/20"),
        KeyboardButton("Cвежезамороженные креветки без панциря 500гр Размер 16 / 20"),
        KeyboardButton("Cвежезамороженные креветки варенные без панциря 500гр Размер 16/20"),
        KeyboardButton("Креветки тигровые С головой Размер-16/20  Блок 1 кг"),
        KeyboardButton("Креветки тигровые Без головы Размер-16/20  Блок 1,44 кг"),
        KeyboardButton("Креветки тигровые Без головы Размер-21/25 Блок 1,44 кг"),
        KeyboardButton("Мидии черные двустворчатые 1 кг"),
        KeyboardButton("Дальневосточный Морской Гребешок 1 кг"),
        KeyboardButton("⬅️ Назад")

    ]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup


def quantity_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("1"),
        KeyboardButton("2"),
        KeyboardButton("3"),
        KeyboardButton("4"),
        KeyboardButton("5"),
        KeyboardButton("6"),
        KeyboardButton("7"),
        KeyboardButton("8"),
        KeyboardButton("9"),
        KeyboardButton("10"),
        KeyboardButton("⬅️ Назад")

    ]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup




def confirm_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Заказать"),
        KeyboardButton("Очистить"),
        KeyboardButton("⬅️ Назад")
    ]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup


def insert_and_back_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Добавить"),
        KeyboardButton("⬅️ Назад")
    ]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup

def insert_and_back_button_admin():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Изменить"),
        KeyboardButton("Удалить"),
        KeyboardButton("⬅️ Назад")
    ]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup


def category_button_all(list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    if len(list) > 0:
        for i in list:
            buttons.append(KeyboardButton(f"{i}"))
        buttons.append(KeyboardButton(f"⬅️ Назад"))
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i + 2])
        return markup

def order_comment():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Отправить и заказать"),
        KeyboardButton("⬅️ Назад")
    ]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i + 2])
    return markup