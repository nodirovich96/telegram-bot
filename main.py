import sqlite3
from datetime import datetime
import telebot
from config import TOKEN, ADMIN_ID
from object import category_list
import logging
from button import (send_photo_button, catalog_button, category_button_all, insert_and_back_button,
                    confirm_button, quantity_button, order_comment)



admin = ADMIN_ID
bot = telebot.TeleBot(TOKEN)




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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Функция вызавается при запуске телеграм бота и проверяет есть ли клиент в базе данных.
       Если клиент не добавлен в базу данных то вызывается функция <<<restourant_name>>>
       В обротном случае вызывается функция <<<catalog_send>>>"""
    con = None
    try:
        bot.send_message(message.chat.id, "Добро пожаловать\n")
        con = conn()
        cursor = con.cursor()
        cursor.execute(f"""SELECT user_id FROM users WHERE user_id = '{message.from_user.id}'""")
        user_id = cursor.fetchall()
        if user_id:
            bot.send_message(message.chat.id, f"Выберите категорию:", reply_markup=catalog_button())
        else:
            bot.send_message(message.chat.id, "Напишите название ресторана\n")
            bot.register_next_step_handler(message, restoraunt_name)

    except Exception as ex:
        bot.send_message(message, f"Возникла ошибка перезапустите бота")

    finally:
        if con:
            con.close()


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    """Функция принимает от пользоватеся контактный номер и проверяет свой номер отправил клиент или нет!
       В случаи если клиент отправил свой номер он делает UPDATE и сохраняет в базу номер телефона"""
    con = None
    try:
        con = conn()
        cursor = con.cursor()

        if message.contact:
            if message.contact.user_id == message.from_user.id:
                phone_number = message.contact.phone_number
                cursor.execute(f"""
                    UPDATE users SET phone = '{message.contact.phone_number}' WHERE user_id = {message.from_user.id}
                """)
                con.commit()

                bot.send_message(message.chat.id, f"Спасибо! Мы получили ваш номер телефона: {phone_number}")
                catalog_send(message)
            else:
                bot.send_message(message.chat.id, "Ошибка: номер телефона не совпадает с вашим аккаунтом.")
        else:
            bot.send_message(message.chat.id, "Вы не отправили номер телефона. Попробуйте снова.")

    except Exception as ex:
        if con:
            con.rollback()
            bot.send_message(message.chat.id, f"Произошла ошибка")
            send_welcome(message)

    finally:
        if con:
            con.close()


@bot.message_handler(content_types=['text'])
def catalog_send(message):
    """Функция отправляет пользователю коталог продуктов!"""
    t_message = message.text
    if message.contact:
        bot.send_message(message.chat.id, f"Выберите категорию:", reply_markup=catalog_button())
    elif t_message in category_list:
        catalog_1(message, t_message)
    elif t_message == "Корзина 🧺":
        cart_get(message)
    elif t_message == "Мои заказы ✅":
        get_orders(message)

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
            bot.send_message(message.chat.id, f"Возникла ошибка")
            send_welcome(message)

    finally:
        if con:
            con.close()



def catalog_1(message, text_message):
    """Функция принимает категорию товара и возвращяет список товаров принадлежащая к этой категории"""
    product_list = []
    con = None
    try:
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
            bot.send_photo(message.chat.id, photo, caption="<b>Выберите продукт</b>⬇️", parse_mode="HTML",
                           reply_markup=category_button_all(product_list))
        bot.register_next_step_handler(message, catalog1_product)

    except Exception as ex:
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
        if message.text == "⬅️ Назад":
            bot.send_message(message.chat.id, f"Выберите категорию:", reply_markup=catalog_button())
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
                                 f"Товар: <b>{product[0][0]}</b>\n\n Цена товара: <b>{product[0][1]:,} сум</b>".replace(
                                     ',', ' '),
                                 reply_markup=insert_and_back_button(), parse_mode="HTML")
                bot.register_next_step_handler(message, insert_or_back, product[0][0], product[0][2])
            else:
                bot.send_message(message.chat.id,
                                 f"Введенные данные не соответствуют требуемому формату. Попробуйте снова.",
                                 reply_markup=catalog_button())
                #catalog_1(message, product[0][2])

    except Exception as ex:
        logging.info(f'Ошибка {ex}')

    finally:
        if con:
            con.close()


def insert_or_back(message, product, category_name):
    """Функция проверяет если клиет нажал на кнопку добавить товар то бот запрашивает количество после чего вызывается
       функция <<<insert_data>>>, а если клиент нажал на конку назад то вызовится функция <<<catalog_1>>>"""
    if message.text == "Добавить":
        bot.send_message(message.chat.id, f"Выберите или напишите количество: ", reply_markup=quantity_button())
        bot.register_next_step_handler(message, insert_data, product, category_name)

    elif message.text == "⬅️ Назад":
        catalog_1(message, category_name)

    else:
        catalog1_product(message)


def insert_data(message, product, category):
    """Функция принимает навзание продукта и добавляет в базу CART (user_id, product_id, quantity),
       количество он получает из последнего сообщения клиента"""
    con = None
    try:
        if message.text == "⬅️ Назад":
            catalog_1(message, category)
        elif int(message.text):
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
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (message.from_user.id, category_id[0][0], int(message.text)))
            con.commit()
            bot.send_message(message.chat.id, f"Товар {product} добавлен в Корзину!")
            catalog_1(message, category_id[0][1])


    except Exception as ex:
        if con:
            con.rollback()
        bot.send_message(message.chat.id,
                         f"Введенные данные не соответствуют требуемому формату. Попробуйте снова.",
                         reply_markup=catalog_button())
        catalog_1(message, category)

    finally:
        if con:
            con.close()
        #catalog_1(message, category_id[0][1])


def cart_get(message):
    con = None
    cart = ""
    cart_to_admin = ""
    try:
        con = conn()
        cursor = con.cursor()
        cursor.execute("""
            SELECT product_name, price, quantity, quantity * price, phone, restaurant_name 
            FROM cart 
            JOIN product USING(product_id) 
            JOIN users USING(user_id) 
            WHERE user_id = ?
        """, (message.from_user.id,))
        product = cursor.fetchall()
        if product:
            for i in range(len(product)):
                cart += (
                    f"Продукт: <b>{product[i][0]}</b>\nЦена: <b>{product[i][1]:,} сум!</b>\n"
                    f"Количество: <b>{product[i][2]}\n</b>"
                    f"Итого: <b>{product[i][3]:,}</b> сум\n\n").replace(',', ' ')
            cart_to_admin += f"{cart}Реcторан: <b>{product[0][5]}</b>\nНомер телефона: <b>{product[0][4]}</b>"
            bot.send_message(message.chat.id, f"{cart}", reply_markup=confirm_button(), parse_mode="HTML")
            bot.register_next_step_handler(message, confirm, cart_to_admin)
        else:
            bot.send_message(message.chat.id, f"Корзина пуста!", reply_markup=catalog_button())


    except Exception as ex:
        if con:
            con.rollback()

    finally:
        if con:
            con.close()

@bot.message_handler(content_types=['text'])
def confirm(message, cart):
    con = None
    try:
        if message.text == "⬅️ Назад":
            bot.send_message(message.chat.id, f"Выберите категорию:", reply_markup=catalog_button())
            catalog_send(message)
        elif message.text == "Очистить":
            con = conn()
            cursor = con.cursor()
            cursor.execute(f"""DELETE FROM cart WHERE user_id = {message.from_user.id}""")
            con.commit()
            bot.send_message(message.chat.id, f"Корзина очищена!", reply_markup=catalog_button())
            catalog_send(message)
        elif message.text == "Заказать":
            bot.send_message(message.chat.id, f"Напишите комментарий к заказу", reply_markup=order_comment())
            bot.register_next_step_handler(message, order, cart)

        else:
            bot.send_message(message.chat.id, f"Не правильный выбор", reply_markup=catalog_button())
            catalog_send(message)

    except Exception as ex:
        if con:
            con.rollback()
            bot.send_message(message, f"Произошла ошибка")
            catalog_send(message)

    finally:
        if con:
            con.close()


def order(message, cart):
    con = None
    try:
        if message.text == '⬅️ Назад':
            bot.send_message(message.chat.id, f"Выберите категорию:", reply_markup=catalog_button())
            catalog_send(message)

        elif message.text == 'Отправить и заказать':
            date_now = datetime.now().date()
            date_format = date_now.strftime("%d-%m-%Y")
            date_str = str(date_format)
            con = conn()
            cursor = con.cursor()
            cursor.execute(f"""INSERT INTO orders (user_id, order_details, date) 
                                            VALUES (?, ?, ?)""",
                           (message.from_user.id, cart, date_str))
            order_id = cursor.lastrowid
            cart = f'ID Заказа: {order_id}\n{cart}'
            cursor.execute(f"""
                INSERT INTO order_details (user_id, product_id, quantity) SELECT user_id, product_id, quantity FROM 
                cart WHERE user_id = {message.from_user.id}
            """)
            cursor.execute(f"""DELETE FROM cart WHERE user_id = {message.from_user.id}""")
            con.commit()
            bot.send_message(message.chat.id, f"Ваш заказ принят!", reply_markup=catalog_button())
            bot.send_message(admin, cart, parse_mode="HTML")
            catalog_send(message)

        else:
            date_now = datetime.now().date()
            date_format = date_now.strftime("%d-%m-%Y")
            date_str = str(date_format)
            bot.send_message(message.chat.id, f"Ваш заказ принят!", reply_markup=catalog_button())
            con = conn()
            cursor = con.cursor()
            cursor.execute(f"""INSERT INTO orders (user_id, order_details, date, comment) 
                                VALUES (?, ?, ?, ?)""", (message.from_user.id, cart, date_str, message.text))
            order_id = cursor.lastrowid
            cart = f'ID Заказа: {order_id}\n{cart}\nКомментарий: {message.text}'
            cursor.execute(f"""
                            INSERT INTO order_details (user_id, product_id, quantity) SELECT user_id, product_id, quantity FROM 
                            cart WHERE user_id = {message.from_user.id}
                        """)
            cursor.execute(f"""DELETE FROM cart WHERE user_id = {message.from_user.id}""")
            con.commit()
            bot.send_message(admin, cart, parse_mode="HTML")
            catalog_send(message)

    except Exception as ex:
        if con:
            con.rollback()
            bot.send_message(message.chat.id, f"Произошла ошибка")
            catalog_send(message)

    finally:
        if con:
            con.close()


def get_orders(message):
    con = None
    try:
        con = conn()
        cursor = con.cursor()
        cursor.execute(f"""SELECT orders_id, order_details, date, comment FROM orders 
                        WHERE user_id = {message.from_user.id} ORDER BY orders_id DESC LIMIT 5""")
        order = cursor.fetchall()
        if order:
            for i in order[::-1]:
                send_order = f"ID Заказа: <b>{i[0]}\n{i[1]}</b>\nДата заказа: <b>{i[2]}г.</b>\nКомментарий: <b>{i[3]}</b>"
                bot.send_message(message.chat.id, send_order, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Ваш список заказов пуст!")
    except Exception:
        print(f"Ошибка")
        if con:
            con.close()


if __name__ == "__main__":
    try:
        print("Запуск бота!")
        bot.infinity_polling()
    except Exception as ex:
        logging.info(f'Ошибка {ex}')
