import sqlite3
import telebot
from telebot.types import ReplyKeyboardRemove
from config import ADMIN_TOKEN, ADMIN_ID
from object import category_list
from button import (send_photo_button, catalog_button_for_admin, category_button_all, insert_and_back_button_admin,
                    quantity_button, back, add_product_for_admin)
import pandas as pd




admin = ADMIN_ID

bot = telebot.TeleBot(ADMIN_TOKEN)

def conn():
    """Функция возвращяет подключение к БД SQLite"""
    con = None
    try:
        con = sqlite3.connect('marketdb.db')
        return con
    except Exception:
        if con:
            con.close()
        return False

@bot.message_handler(commands=['get_db'])
def get_db(message):
    try:
        if message.from_user.id == admin:
            path = 'marketdb.db'
            bot.send_document(message.chat.id, document=open(path,'rb'), visible_file_name="marketdb.db")
        else:
            bot.send_message(message.chat.id, 'Доступ ограничен для других пользователей!')

    except Exception as ex:
        bot.send_message(message.chat.id, f'Возникла ошибка! {ex}')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Функция вызавается при запуске телеграм бота и проверяет есть ли клиент в базе данных.
       Если клиент не добавлен в базу данных то вызывается функция <<<restourant_name>>>
       В обротном случае вызывается функция <<<catalog_send>>>"""
    try:
        if message.from_user.id == admin:
            bot.send_message(message.chat.id, "Добро пожаловать админ!\n", reply_markup=catalog_button_for_admin())
            bot.register_next_step_handler(message, catalog_send)
        else:
            bot.send_message(message.chat.id, "Доступ ограничен для других пользователей!\n")
    except Exception as ex:
        bot.send_message(message, f"Возникла ошибка перезапустите бота {ex}")


@bot.message_handler(content_types=['photo'])
def send_welcome(message):
    try:
        if message.from_user.id == admin:
            bot.send_message(message.chat.id, "Выберите категоврию где хотите поменять/добавить фото",
                                                    reply_markup= add_product_for_admin())

            bot.register_next_step_handler(message, save_photo, message.photo[-1])
        else:
            bot.send_message(message.chat.id, "Доступ ограничен для других пользователей!\n")
    except Exception as ex:
        bot.send_message(message, f"Возникла ошибка перезапустите бота {ex}")

def save_photo(message, photo):
    con = None
    try:
        if message.text == '⬅️ Назад':
            bot.send_message(admin, f"Выберите категорию", reply_markup=catalog_button_for_admin())
        else:
            con = conn()
            cursor = con.cursor()
            cursor.execute("""SELECT category_id FROM category WHERE category_name = ?""", (message.text,))
            category_id = cursor.fetchall()
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = f'images/{category_id[0][0]}.jpg'
            with open(file_path, "wb") as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, f'Вы поменяли фото!', reply_markup=catalog_button_for_admin())


    except Exception as ex:
        bot.send_message(message.chat.id, f'Возникла ошибка {ex}', reply_markup=catalog_button_for_admin())

    finally:
        if con:
            con.close()


@bot.message_handler(content_types=['text'])
def catalog_send(message):
    """Функция отправляет пользователю коталог продуктов!"""
    t_message = message.text
    if t_message in category_list and message.from_user.id == admin:
        catalog_1(message, t_message)
    elif t_message == "Корзина 🧺" and message.from_user.id == admin:
        cart_get(message)
    elif t_message == "Добавить товар" and message.from_user.id == admin:
        bot.send_message(admin, f"В какую категорию добавим товар?", reply_markup=add_product_for_admin())
        bot.register_next_step_handler(message, new_product)
    elif t_message == "Отчет по продажам" and message.from_user.id == admin:
        dataframe(message)
    elif t_message == "Изменить фото категории" and message.from_user.id == admin:
        bot.send_message(admin, f"Отправьте фото")



def dataframe(message):
    con = None
    try:
        con = conn()
        df = pd.read_sql("""SELECT user_id, user_name, phone, restaurant_name, category_name, product_name, discontinued, price, quantity, 
        (price * quantity) as total_price, date FROM users JOIN order_details USING(user_id) JOIN product USING(product_id) 
         JOIN category USING(category_id)""", con)
        if df.empty:
            bot.send_message(admin, f'DataFrame пустой')
        else:
            df = df.rename(columns={
                'user_id': 'Идентификатор пользователя',
                'user_name': 'Имя пользователя',
                'phone': 'Номер телефона',
                'restaurant_name': 'Название ресторана',
                'category_name': 'Категория товара',
                'product_name': 'Название товара',
                'discontinued': 'Статус товара',
                'price': 'Цена за ед.',
                'quantity': 'Количество',
                'total_price': 'Сумма',
                'date': 'Дата заказа'
            })

            df.to_csv('dataframe/DataFrame.csv', sep=";", encoding="cp1251", index=False)
            with open('dataframe/DataFrame.csv', 'rb') as file:
                bot.send_document(admin, file)

    except Exception as ex:
        bot.send_message(admin, f'Ошибка {ex}')
    finally:
        if con:
            con.close()


def new_product(message):
    try:
        if message.text == '⬅️ Назад':
            bot.send_message(admin, f"Выберите категорию", reply_markup=catalog_button_for_admin())

        elif message.text in category_list and message.from_user.id == admin:
            bot.send_message(message.chat.id, 'Напишите название товара', reply_markup=back())
            bot.register_next_step_handler(message, product_name, message.text)

        else:
            bot.send_message(message.chat.id, 'Такой категории нет', reply_markup=catalog_button_for_admin())
    except Exception as ex:
        bot.send_message(message.chat.id, f'Возникла ошибка {ex}', reply_markup=catalog_button_for_admin())

def product_name(message, category_name):
    try:
        if message.text == '⬅️ Назад':
            bot.send_message(admin, f"Выберите категорию", reply_markup=catalog_button_for_admin())
        else:
            bot.send_message(admin, f"Цена товара", reply_markup=back())
            bot.register_next_step_handler(message, add_product, category_name,
                                                                  message.text)

    except Exception as ex:
        bot.send_message(admin, f"Возникла ошибка {ex}", reply_markup=catalog_button_for_admin())
            

def add_product(message, *args):
    con = conn()
    try:
        if message.text == '⬅️ Назад':
            bot.send_message(admin, f"Выберите категорию", reply_markup=catalog_button_for_admin())
        elif int(message.text.replace(' ','')):
            con = conn()
            cursor = con.cursor()
            cursor.execute("""SELECT category_id FROM category WHERE category_name = ?""", (args[0],))
            category_id = cursor.fetchall()
            cat_id_int = int(category_id[0][0])
            cursor.execute("""INSERT INTO product (category_id, product_name, price) VALUES (?, ?, ?)""",
                           (cat_id_int, args[1], int(message.text.replace(' ',''))))
            con.commit()
            bot.send_message(admin, f"Новый товар добавлен!", reply_markup=catalog_button_for_admin())
        else:
            bot.send_message(admin, f"Ошибка", reply_markup=catalog_button_for_admin())

    except Exception as ex:
        bot.send_message(admin, f"Возникла ошибка {ex}", reply_markup=catalog_button_for_admin())
        if con:
            con.rollback()

    finally:
        if con:
            con.close()


def restoraunt_name(message):
    """Функция принимает текстовое сообщение о названии ресторана и
    сохраняет в базу данные (USER_ID, RESTOURANT_NAME, USER_NAME)!"""
    t_message = message.text
    con = None
    try:
        con = conn()
        cursor = con.cursor()
        cursor.execute(f"""INSERT INTO users (user_id, restaurant_name, user_name) 
            VALUES ({message.from_user.id},'{t_message}', '{message.from_user.username}')""")
        con.commit()
        bot.send_message(message.chat.id, "Отправьте свой номер!", reply_markup=send_photo_button())

    except Exception as ex:
        if con:
            con.rollback()
            bot.send_message(message.chat.id, f"Возникла ошибка {ex}")
            send_welcome(message)

    finally:
        if con:
            con.close()



def catalog_1(message, text_message):
    """Функция принимает категорию товара и возвращяет список товаров принадлежащая к этой категории"""
    product_list = []
    con = None
    try:
        if message.from_user.id == admin:
            con = conn()
            cursor = con.cursor()
            cursor.execute("""
                SELECT product_name, category_id
                FROM product
                JOIN category USING(category_id)
                WHERE category_name = ? AND discontinued = 1
            """, (text_message,))
            product = cursor.fetchall()
            for i in range(len(product)):
                product_list.append(product[i][0])
            category_photo = product[0][1]
            with open(f'images/{category_photo}.jpg', 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption="Выберите продукт",
                               reply_markup=category_button_all(product_list))
            bot.register_next_step_handler(message, catalog1_product)
        else:
            bot.send_message(message.chat.id, f"Вы не админ")

    except Exception:
        if con:
            con.rollback()
    finally:
        if con:
            con.close()


def catalog1_product(message):

    """Функция проверит на какой продукт нажал пользователь и сравнивает есть ли такой товар в базе данных.
       Если есть то вызывается функция <<<insert_or_back>>>, а если клиент нажал на кнопку назад то
       отправляет его в меню каталога!"""
    con = None
    try:
        if message.from_user.id == admin:
            if message.text == "⬅️ Назад":
                bot.send_message(message.chat.id, "Выберите категоврию!\n", reply_markup=catalog_button_for_admin())
                catalog_send(message)
            elif message.text != "⬅️ Назад":
                con = conn()
                cursor = con.cursor()
                cursor.execute("""
                    SELECT product_name, price, category_name
                    FROM product
                    JOIN category USING(category_id)
                    WHERE product_name = ? AND discontinued = 1
                """, (message.text,))
                product = cursor.fetchall()
                if product:
                    bot.send_message(message.chat.id,
                                     f"Товар: <b>{product[0][0]}</b>\n\n"
                                     f" Цена товара: <b>{product[0][1]:,} сум</b>".replace(',', ' '),
                                     reply_markup=insert_and_back_button_admin(), parse_mode="HTML")
                    bot.register_next_step_handler(message, insert_or_back, product[0][0], product[0][2])
                else:
                    bot.send_message(message.chat.id,
                                     f"Введенные данные не соответствуют требуемому формату. Попробуйте снова.",
                                     reply_markup=catalog_button_for_admin())
                    #catalog_1(message, product[0][2])
        else:
            bot.send_message(message.chat.id, f"Вы не админ")

    except Exception as ex:
        print("Ошибка")

    finally:
        if con:
            con.close()


def insert_or_back(message, product, category_name):
    """Функция проверяет если клиет нажал на кнопку добавить товар то бот запрашивает количество после чего вызывается
       функция <<<insert_data>>>, а если клиент нажал на конку назад то вызовится функция <<<catalog_1>>>"""
    if message.from_user.id == admin:
        if message.text == "Изменить":
            bot.send_message(message.chat.id, f"Напишите новую цену: ", reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(message, insert_data, product, category_name)

        elif message.text == "⬅️ Назад":
            catalog_1(message, category_name)
        elif message.text == "Удалить":
            delete_product(message,product)
        else:
            catalog1_product(message)
    else:
        bot.send_message(message.chat.id, f"Вы не админ")

def delete_product(message, product):
    con = conn()
    try:
        con = conn()
        cursor = con.cursor()
        cursor.execute("""SELECT product_id FROM product WHERE product_name = ? AND discontinued = 1
                                ORDER BY product_id DESC LIMIT 1""", (product,))
        prod_id = cursor.fetchall()
        cursor.execute("""UPDATE product SET discontinued = 0 WHERE product_id = ?""", (prod_id[0][0],))
        cursor.execute("""DELETE FROM cart WHERE product_id = ?""", (prod_id[0][0],))
        con.commit()
        bot.send_message(message.chat.id, f"Товар удалён", reply_markup=catalog_button_for_admin())


    except Exception as ex:
        bot.send_message(message.chat.id, f"Возникла ошибка {ex}", reply_markup=catalog_button_for_admin())
        if con:
            con.rollback()

    finally:
        if con:
            con.close()


def insert_data(message, product, category):
    """Функция принимает навзание продукта и добавляет в базу CART (user_id, product_id, quantity),
       количество он получает из последнего сообщения клиента"""
    con = None
    try:
        if message.text == "⬅️ Назад":
            catalog_1(message, category)

        elif message.from_user.id == admin:
            if int(message.text):
                con = conn()
                cursor = con.cursor()
                cursor.execute("""
                    SELECT product_id, category_name
                    FROM product
                    JOIN category USING(category_id)
                    WHERE product_name = ? AND discontinued = 1
                """, (product,))
                category_id = cursor.fetchall()
                cursor.execute("""
                    UPDATE product SET price = ?
                    WHERE product_name = ? AND discontinued = 1
                """, (int(message.text), product))
                con.commit()
                bot.send_message(message.chat.id, f"Товар: {product}\nНовая цена: {message.text} сум")
                catalog_1(message, category_id[0][1])
        else:
            bot.send_message(message.chat.id, f"Вы не админ")

    except Exception as ex:
        if con:
            con.rollback()
        bot.send_message(message.chat.id,
                         f"Введенные данные не соответствуют требуемому формату. Попробуйте снова.",
                         reply_markup=catalog_button_for_admin())
        catalog_1(message, category)

    finally:
        if con:
            con.close()



def cart_get(message):
    con = None
    cart = ""
    try:
        if message.from_user.id == admin:
            con = conn()
            cursor = con.cursor()
            cursor.execute("""
                SELECT product_name, price, quantity, quantity * price, phone, restaurant_name 
                FROM cart 
                JOIN product USING(product_id) 
                JOIN users USING(user_id)
            """)
            product = cursor.fetchall()
            if product:
                for i in range(len(product)):
                    cart += (
                        f"Продукт: <b>{product[i][0]}</b>\nЦена: <b>{product[i][1]:,} сум!</b>\n"
                        f"Количество: <b>{product[i][2]}\n</b>"
                        f"Итого: <b>{product[i][3]:,}</b> сум\n\nРеcторан: <b>{product[0][5]}</b>\n"
                        f"Номер телефона: <b>{product[0][4]}</b>").replace(',', ' ')
                bot.send_message(admin, f"{cart}", reply_markup=catalog_button_for_admin(), parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, f"Корзина пуста!", reply_markup=catalog_button_for_admin())
        else:
            bot.send_message(message.chat.id, f"вы не админ!")

    except Exception as ex:
        bot.send_message(admin, f"Произошла ошибка{ex}", reply_markup=catalog_button_for_admin())

    finally:
        if con:
            con.close()


if __name__ == "__main__":
    try:
        print("Запуск бота!")
        bot.infinity_polling()
    except Exception as ex:
        print(f"Произошла ошибка {ex}")
