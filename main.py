# -*- coding: utf-8 -*-

from config import token
import telebot
import sqlite3 as sl
from random import choice

bot = telebot.TeleBot(token)


conn = sl.connect("users.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS Users
                  (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL,
                  user_name TEXT NOT NULL)
               """)
conn.commit()
conn.close()

lenta_flag = 0 # флаг даёт понять, что выбран магазин лента
p_flag = 0 # флаг даёт понять, что выбран магазин пятёрочка
mariara_flag = 0 # флаг даёт понять, что выбран магазин мария-ра
msg1 = None # глобальная переменная для изменения/удаления сообщения "Итоговый список:"
msg2 = None # глобальная переменная для изменения/удаления сообщения с выводом итогового списка

products = ['Шоколад','Вафли','Сладкий попкорн','Сырки','Киндер-батончик','Конфеты метелица','Чипсы','Крекеры Тук','Гренки с красной икрой','Сыр косичка','Солёный попкорн','Сырный попкорн','Сырные шарики','Корнишоны','Рыба в баночке','Бычки в томате','Солёная селедка','Копчёная селедка','Копчёная красная рыба','Набор морепродуктов в баночке','Чука в ореховом соусе', 'Энергетик','Томатный сок','Лимонад','Вишнёвый сок','Бутерброд ветчина с сыром','Сырный багет','Слойка с курицей','Слойка с ветчиной','Ёжик со сгущёнкой', 'Вафельные трубочки', 'Шоколадные вафли', 'Вафли со сгущёнкой', 'Бутерброды из ленты', 'Сухая картошка']
products_delete = [i + "_delete" for i in products] # список для проверки удалённых позиций
result_list = [] # итоговый список покупок

# Все переменные ниже нужны для случайного выбора списка покупок
products_candies = ['Шоколад','Сладкий попкорн','Сырки','Киндер-батончик','Конфеты метелица', 'Вафельные трубочки', 'Шоколадные вафли', 'Вафли со сгущёнкой']
products_snacks = ['Чипсы','Крекеры Тук','Гренки с красной икрой','Сыр косичка','Солёный попкорн','Сырный попкорн','Сырные шарики','Корнишоны', 'Сухая картошка']
products_snacks_lenta = ['Чипсы','Крекеры Тук','Гренки с красной икрой','Сыр косичка','Солёный попкорн','Сырный попкорн','Сырные шарики','Корнишоны', 'Сухая картошка', 'Бутерброды из ленты']
products_fish = ['Рыба в баночке','Бычки в томате','Солёная селедка','Копчёная селедка','Копчёная красная рыба','Набор морепродуктов в баночке','Чука в ореховом соусе']
products_drinks = ['Энергетик','Томатный сок','Лимонад','Вишнёвый сок']
products_bakery_5 = 'Бутерброд ветчина с сыром'
products_bakery_mariara = ['Сырный багет','Слойка с курицей','Слойка с ветчиной','Ёжик со сгущёнкой']

# Старт бота, проверка пользователя в базе данных и регистрация
@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    print(f'Авторизация пользователя #{chat_id}.')

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    restart = telebot.types.KeyboardButton(text='Перезапуск бота')
    cookie = telebot.types.KeyboardButton(text='Вкусняшки')
    name_change = telebot.types.KeyboardButton(text='Поменять имя')
    keyboard.add(restart, cookie, name_change)

    if db_search_id(chat_id):
        bot.send_message(chat_id, f'{db_get_username(chat_id)}, я тебя категорически приветствую!', reply_markup=keyboard)
    else:
        bot.send_message(chat_id, 'Ну привет, как тебя зовут?')
        bot.register_next_step_handler(message, save_username)


# реализация проверки пользователя в базе данных
def db_search_id(user_id: int):
    users = sl.connect('users.db')
    users_cursor = users.cursor()
    users_cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
    uid = users_cursor.fetchone()

    if uid is None:
        print(f'Пользователь #{user_id} не найден.')
        users.close()
        return 0

    else:
        print(f'Пользователь #{user_id} найден.')
        users.close()
        return uid[0]


# вывод имени пользователя из базы данных по id пользователя
def db_get_username(user_id: int):
    users = sl.connect('users.db')
    users_cursor = users.cursor()
    users_cursor.execute("SELECT user_name FROM Users WHERE user_id = ?", (user_id,))
    name = users_cursor.fetchone()[0]
    users.close()
    return name


# создание имени пользователя
def save_username(message):
    chat_id = message.chat.id
    name = message.text
    users = sl.connect('users.db')
    users_cursor = users.cursor()
    users_cursor.execute('INSERT INTO Users (user_id, user_name) VALUES (?, ?)', (chat_id, name))
    print(f'Пользователь #{chat_id} успешно добавлен.')
    users.commit()
    users.close()
    bot.send_message(chat_id, f'Отлично, {name}. Что дальше?')


# смена имени пользователя
@bot.message_handler(commands=['change_name'])
def change_name(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите новое имя:')
    bot.register_next_step_handler(message, db_change_username)


# изменение имени пользователя в базе данных
def db_change_username(message):
    chat_id = message.chat.id
    new_name = message.text
    users = sl.connect('users.db')
    users_cursor = users.cursor()
    users_cursor.execute('Update Users set user_name = ? where user_id = ?', (new_name, chat_id))
    print(f'Пользователь #{chat_id} успешно сменил имя.')
    bot.send_message(chat_id, f'Имя пользователя успешно изменено на: {new_name}')
    users.commit()
    users.close()


@bot.message_handler(commands=['cookies'])
def cookies(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    lenta = telebot.types.InlineKeyboardButton(text="Лента", callback_data="lenta_data")
    maria_ra = telebot.types.InlineKeyboardButton(text="Мария-ра", callback_data="mariara_data")
    pyaterochka = telebot.types.InlineKeyboardButton(text="Пятёрочка", callback_data="5_data")
    keyboard.add(lenta, maria_ra, pyaterochka)
    bot.send_message(chat_id, 'Выберите магазин:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "5_data")
def shop_5(call):
    global lenta_flag, p_flag, mariara_flag
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    call_id = call.id

    mariara_flag = 0
    lenta_flag = 0
    p_flag = 1

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    candies = telebot.types.InlineKeyboardButton(text="Сладкое", callback_data="5_candies_data")
    salty = telebot.types.InlineKeyboardButton(text="Солёное", callback_data="5_salty_data")
    drinks = telebot.types.InlineKeyboardButton(text="Напитки", callback_data="5_drinks_data")
    bakery = telebot.types.InlineKeyboardButton(text="Выпечка", callback_data="5_bakery_data")
    rand_choice = telebot.types.InlineKeyboardButton(text="Случайный выбор", callback_data="Случайный выбор")
    keyboard.add(candies, salty, drinks, bakery)
    keyboard.add(rand_choice)

    bot.answer_callback_query(call_id, 'Выбран магазин Пятёрочка!')
    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, "Выберите категорию:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "lenta_data")
def lenta_shop(call):
    global lenta_flag, p_flag, mariara_flag
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    call_id = call.id

    mariara_flag = 0
    lenta_flag = 1
    p_flag = 0

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    candies = telebot.types.InlineKeyboardButton(text="Сладкое", callback_data="lenta_candies_data")
    salty = telebot.types.InlineKeyboardButton(text="Солёное", callback_data="lenta_salty_data")
    drinks = telebot.types.InlineKeyboardButton(text="Напитки", callback_data="lenta_drinks_data")
    rand_choice = telebot.types.InlineKeyboardButton(text="Случайный выбор", callback_data="Случайный выбор")
    keyboard.add(candies, salty, drinks)
    keyboard.add(rand_choice)

    bot.answer_callback_query(call_id, 'Выбран магазин Лента!')
    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, "Выберите категорию:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "mariara_data")
def marira_shop(call):
    global lenta_flag, p_flag, mariara_flag
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    call_id = call.id

    mariara_flag = 1
    lenta_flag = 0
    p_flag = 0

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    candies = telebot.types.InlineKeyboardButton(text="Сладкое", callback_data="mariara_candies_data")
    salty = telebot.types.InlineKeyboardButton(text="Солёное", callback_data="mariara_salty_data")
    drinks = telebot.types.InlineKeyboardButton(text="Напитки", callback_data="mariara_drinks_data")
    bakery = telebot.types.InlineKeyboardButton(text="Выпечка", callback_data="mariara_bakery_data")
    rand_choice = telebot.types.InlineKeyboardButton(text="Случайный выбор", callback_data="Случайный выбор")
    keyboard.add(candies, salty, drinks, bakery)
    keyboard.add(rand_choice)

    bot.answer_callback_query(call_id, 'Выбран магазин Мария-ра!')
    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, "Выберите категорию:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["Случайный выбор", "again"])
def random_choice(call):
    global lenta_flag, p_flag, mariara_flag, msg1, msg2, result_list
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    if call.data == 'again':
        bot.delete_message(chat_id, msg1.message_id)
        bot.delete_message(chat_id, msg2.message_id)
        result_list = []

    result_list.append(choice(products_candies))
    if lenta_flag:
        result_list.append(choice(products_snacks_lenta))
    else:
        result_list.append(choice(products_snacks))
    result_list.append(choice(products_fish))
    result_list.append(choice(products_drinks))
    if p_flag:
        result_list.append(products_bakery_5)
    elif mariara_flag:
        result_list.append(choice(products_bakery_mariara))

    msg1 = bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Итоговый список покупок:')
    msg2 = bot.send_message(chat_id, '\n'.join(map(str, result_list)))
    keyboard = telebot.types.InlineKeyboardMarkup()
    yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    return_to_choice = telebot.types.InlineKeyboardButton(text='Вернуться к выбору', callback_data='Вернуться к выбору')
    again = telebot.types.InlineKeyboardButton(text='Попробовать ещё раз', callback_data='again')
    keyboard.add(yes, no)
    keyboard.add(return_to_choice)
    keyboard.add(again)

    bot.send_message(chat_id, 'Всё верно?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["5_candies_data", "lenta_candies_data", "mariara_candies_data", "lenta_next_button", "snacks_back_button", "5_next_button", "mariara_next_button", "Вернуться к выбору"])
def candies_category(call):
    global lenta_flag, msg1, msg2
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id


    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    chocolate = telebot.types.InlineKeyboardButton(text='Шоколад', callback_data='Шоколад')
    waffles = telebot.types.InlineKeyboardButton(text='Вафли', callback_data='Вафли')
    popcorn = telebot.types.InlineKeyboardButton(text='Сладкий попкорн', callback_data='Сладкий попкорн')
    sirky = telebot.types.InlineKeyboardButton(text='Сырки', callback_data='Сырки')
    kinder_baton = telebot.types.InlineKeyboardButton(text='Киндер-батончик', callback_data='Киндер-батончик')
    metel = telebot.types.InlineKeyboardButton(text='Конфеты метелица', callback_data='Конфеты метелица')

    next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='candies_next_button')
    back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='candies_back_button')
    l_back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='lenta_back_button')

    end_of_choice = telebot.types.InlineKeyboardButton(text="Закончить выбор продуктов", callback_data='end_of_choice')

    if call.data == 'Вернуться к выбору':
        bot.delete_message(chat_id, msg1.message_id)
        bot.delete_message(chat_id, msg2.message_id)

    if lenta_flag:
        keyboard.add(chocolate, waffles, popcorn, sirky, kinder_baton, metel)
        keyboard.add(next_button, l_back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,text='Выберите сладости:', reply_markup=keyboard)
    else:
        keyboard.add(chocolate, waffles, popcorn, sirky, kinder_baton, metel)
        keyboard.add(next_button, back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите сладости:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["5_salty_data", "lenta_salty_data", "mariara_salty_data"])
def salty_category(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    if call.data == "5_salty_data":
        snacks = telebot.types.InlineKeyboardButton(text="Снэки", callback_data="5_snacks_data")
        fish = telebot.types.InlineKeyboardButton(text="Рыба и морепродукты", callback_data="5_fish_data")
        keyboard.add(snacks, fish)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Что именно?", reply_markup=keyboard)

    elif call.data == "lenta_salty_data":
        snacks = telebot.types.InlineKeyboardButton(text="Снэки", callback_data="lenta_snacks_data")
        fish = telebot.types.InlineKeyboardButton(text="Рыба и морепродукты", callback_data="lenta_fish_data")
        keyboard.add(snacks, fish)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Что именно?", reply_markup=keyboard)

    elif call.data == "mariara_salty_data":
        snacks = telebot.types.InlineKeyboardButton(text="Снэки", callback_data="mariara_snacks_data")
        fish = telebot.types.InlineKeyboardButton(text="Рыба и морепродукты", callback_data="mariara_fish_data")
        keyboard.add(snacks, fish)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Что именно?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["5_snacks_data", "lenta_snacks_data", "mariara_snacks_data", "candies_next_button", "fish_back_button"])
def snacks_category(call):
    global lenta_flag
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    chips = telebot.types.InlineKeyboardButton(text='Чипсы', callback_data='Чипсы')
    tuc = telebot.types.InlineKeyboardButton(text='Крекеры Тук', callback_data='Крекеры Тук')
    grenky = telebot.types.InlineKeyboardButton(text='Гренки с красной икрой', callback_data='Гренки с красной икрой')
    sir_kos = telebot.types.InlineKeyboardButton(text='Сыр косичка', callback_data='Сыр косичка')
    popcorn_salty = telebot.types.InlineKeyboardButton(text='Солёный попкорн', callback_data='Солёный попкорн')
    popcorn_cheese = telebot.types.InlineKeyboardButton(text='Сырный попкорн', callback_data='Сырный попкорн')
    cheese_balls = telebot.types.InlineKeyboardButton(text='Сырные шарики', callback_data='Сырные шарики')
    kornish = telebot.types.InlineKeyboardButton(text='Корнишоны', callback_data='Корнишоны')
    potato = telebot.types.InlineKeyboardButton(text='Сухая картошка', callback_data='Сухая картошка')
    buter = telebot.types.InlineKeyboardButton(text='Бутерброды из ленты', callback_data='Бутерброды из ленты')

    next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='snacks_next_button')
    back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='snacks_back_button')
    end_of_choice = telebot.types.InlineKeyboardButton(text="Закончить выбор продуктов", callback_data='end_of_choice')

    if lenta_flag:
        keyboard.add(chips, tuc, grenky, sir_kos, popcorn_salty, popcorn_cheese, cheese_balls, kornish, potato, buter)
        keyboard.add(next_button, back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите снэки:', reply_markup=keyboard)
    else:
        keyboard.add(chips, tuc, grenky, sir_kos, popcorn_salty, popcorn_cheese, cheese_balls, kornish, potato)
        keyboard.add(next_button, back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите снэки:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["5_fish_data", "lenta_fish_data", "mariara_fish_data", "snacks_next_button", "drinks_back_button"])
def fish_category(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    fish_in_ban = telebot.types.InlineKeyboardButton(text='Рыба в баночке', callback_data='Рыба в баночке')
    bich_in_tomate = telebot.types.InlineKeyboardButton(text='Бычки в томате', callback_data='Бычки в томате')
    salty_seled = telebot.types.InlineKeyboardButton(text='Солёная селедка', callback_data='Солёная селедка')
    copch_seled = telebot.types.InlineKeyboardButton(text='Копчёная селедка', callback_data='Копчёная селедка')
    copch_red_fish = telebot.types.InlineKeyboardButton(text='Копчёная красная рыба', callback_data='Копчёная красная рыба')
    moreprod_nabor = telebot.types.InlineKeyboardButton(text='Набор морепродуктов в баночке', callback_data='Набор морепродуктов в баночке')
    chuka_in_oreh = telebot.types.InlineKeyboardButton(text='Чука в ореховом соусе', callback_data='Чука в ореховом соусе')

    next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='fish_next_button')
    back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='fish_back_button')
    end_of_choice = telebot.types.InlineKeyboardButton(text="Закончить выбор продуктов", callback_data='end_of_choice')

    keyboard.add(fish_in_ban, bich_in_tomate, salty_seled, copch_seled, copch_red_fish, moreprod_nabor, chuka_in_oreh)
    keyboard.add(next_button, back_button, end_of_choice)
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите рыбу и морепродукты:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["5_drinks_data", "lenta_drinks_data", "mariara_drinks_data", "fish_next_button", "5_back_button", "mariara_back_button", "lenta_back_button"])
def drinks_category(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    energos = telebot.types.InlineKeyboardButton(text='Энергетик', callback_data='Энергетик')
    tomat_juice = telebot.types.InlineKeyboardButton(text='Томатный сок', callback_data='Томатный сок')
    limonade = telebot.types.InlineKeyboardButton(text='Лимонад', callback_data='Лимонад')
    cherry_juice = telebot.types.InlineKeyboardButton(text='Вишнёвый сок', callback_data='Вишнёвый сок')

    next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='drinks_next_button')
    back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='drinks_back_button')
    l_next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='lenta_next_button')
    end_of_choice = telebot.types.InlineKeyboardButton(text="Закончить выбор продуктов", callback_data='end_of_choice')

    if lenta_flag:
        keyboard.add(energos, tomat_juice, limonade, cherry_juice)
        keyboard.add(l_next_button, back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите напитки:', reply_markup=keyboard)
    else:
        keyboard.add(energos, tomat_juice, limonade, cherry_juice)
        keyboard.add(next_button, back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите напитки:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["5_bakery_data", "mariara_bakery_data", "drinks_next_button", "candies_back_button"])
def bakery_category(call):
    global p_flag, mariara_flag
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    buterbroad = telebot.types.InlineKeyboardButton(text='Бутерброд ветчина с сыром', callback_data='Бутерброд ветчина с сыром')
    baget_cheese = telebot.types.InlineKeyboardButton(text='Сырный багет', callback_data='Сырный багет')
    sloyka_chicken = telebot.types.InlineKeyboardButton(text='Слойка с курицей', callback_data='Слойка с курицей')
    sloyka_vetchina = telebot.types.InlineKeyboardButton(text='Слойка с ветчиной', callback_data='Слойка с ветчиной')
    ejik = telebot.types.InlineKeyboardButton(text='Ёжик со сгущёнкой', callback_data='Ёжик со сгущёнкой')

    p_next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='5_next_button')
    p_back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='5_back_button')

    mariara_next_button = telebot.types.InlineKeyboardButton(text="Следующая категория ->", callback_data='mariara_next_button')
    mariara_back_button = telebot.types.InlineKeyboardButton(text="<- Предыдущая категория", callback_data='mariara_back_button')

    end_of_choice = telebot.types.InlineKeyboardButton(text="Закончить выбор продуктов", callback_data='end_of_choice')

    if p_flag:
        keyboard.add(baget_cheese, sloyka_chicken, sloyka_vetchina, ejik)
        keyboard.add(p_next_button, p_back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите выпечку:', reply_markup=keyboard)
    elif mariara_flag:
        keyboard.add(buterbroad)
        keyboard.add(mariara_next_button, mariara_back_button, end_of_choice)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите выпечку:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in products)
def product_list(call):
    global result_list
    message = call.message
    chat_id = message.chat.id
    call_id = call.id
    message_id = message.message_id

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)

    trub = telebot.types.InlineKeyboardButton(text='Вафельные трубочки', callback_data='Вафельные трубочки')
    waffles_chocolate = telebot.types.InlineKeyboardButton(text='Шоколадные вафли', callback_data='Шоколадные вафли')
    waffles_sguha = telebot.types.InlineKeyboardButton(text='Вафли со сгущёнкой', callback_data='Вафли со сгущёнкой')

    keyboard.add(trub, waffles_chocolate, waffles_sguha)

    for i in products:
        if i == call.data:
            if i == 'Вафли':
                bot.send_message(chat_id, 'Выберите определённые вафли:', reply_markup=keyboard)
            elif i in ['Вафельные трубочки', 'Шоколадные вафли', 'Вафли со сгущёнкой']:
                if i not in result_list:
                    result_list.append(i)
                    bot.answer_callback_query(call_id, f"{i} теперь в списке покупок!")
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                else:
                    bot.answer_callback_query(call_id, f"{i} уже в списке!")
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
            else:
                if i not in result_list:
                    result_list.append(i)
                    bot.answer_callback_query(call_id, f"{i} теперь в списке покупок!")
                else:
                    bot.answer_callback_query(call_id, f"{i} уже в списке!")


@bot.callback_query_handler(func=lambda call: call.data == "end_of_choice")
def product_result(call):
    global msg1, msg2
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    msg1 = bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Итоговый список покупок:')
    msg2 = bot.send_message(chat_id, '\n'.join(map(str, result_list)))
    keyboard = telebot.types.InlineKeyboardMarkup()
    yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    return_to_choice = telebot.types.InlineKeyboardButton(text='Вернуться к выбору', callback_data='Вернуться к выбору')
    keyboard.add(yes, no)
    keyboard.add(return_to_choice)

    bot.send_message(chat_id, 'Всё верно?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no', 'cancel', 'ready'] or call.data in products_delete)
def correct_list(call):
    global result_list, msg2
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    call_id = call.id

    if call.data == 'yes':
        bot.answer_callback_query(call_id, f"Отлично!")
        bot.delete_message(chat_id, message_id)
        result_list = []
    elif call.data == 'no':
        bot.delete_message(chat_id, message_id)
        bot.delete_message(chat_id, msg2.message_id)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        for i in result_list:
            o = telebot.types.InlineKeyboardButton(text=i, callback_data=i+'_delete')
            keyboard.add(o)
        cancel = telebot.types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        keyboard.add(cancel)
        bot.send_message(chat_id, 'Выберите ненужные позиции:', reply_markup=keyboard)
    elif call.data in products_delete:
        result_list.remove(call.data[:len(call.data)-7])
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        for i in result_list:
            o = telebot.types.InlineKeyboardButton(text=i, callback_data=i + '_delete')
            keyboard.add(o)
        ready = telebot.types.InlineKeyboardButton(text='Готово', callback_data='ready')
        keyboard.add(ready)
        bot.edit_message_text(chat_id=chat_id,message_id=message_id, text='Выберите ненужные позиции:', reply_markup=keyboard)
    elif call.data in ['cancel', 'ready']:
        bot.delete_message(chat_id, message_id)
        msg2 = bot.send_message(chat_id, '\n'.join(map(str, result_list)))
        keyboard = telebot.types.InlineKeyboardMarkup()
        yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
        no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
        return_to_choice = telebot.types.InlineKeyboardButton(text='Вернуться к выбору', callback_data='Вернуться к выбору')
        keyboard.add(yes, no)
        keyboard.add(return_to_choice)

        bot.send_message(chat_id, 'Всё верно?', reply_markup=keyboard)

if __name__ == '__main__':
    print('Запуск прошёл успешно!')
    bot.infinity_polling()