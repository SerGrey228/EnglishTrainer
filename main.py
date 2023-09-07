import telebot
from telebot import types
import sqlite3 as sq

bot = telebot.TeleBot("6506952494:AAGkRc8JVZyV9sWI2qxkHjpuYqer35DTuSg")
adminRule = False

@bot.message_handler(commands=["lean"])
def lean(message):
    with sq.connect("dictionary.db") as con:
        cur = con.cursor()

        size_table = cur.execute("SELECT COUNT (*) FROM words").fetchone() # количество строк в таблице

    with sq.connect("dictionary.db") as con:
        cur = con.cursor()
        i = 1
        list_numbers = []

        cur.execute(f"SELECT * FROM words")
        for w in cur.fetchall():
            bot.send_message(message.chat.id, f"Введите перевод к слову {w[1]}")
            bot.register_next_step_handler(message, check_pass)

@bot.message_handler(commands=["start"])
def start(message):

    # with sq.connect("dictionary.db") as con:
    #     cur = con.cursor()
    #
    #     # создание таблицы Слова в базе данных если она не создана
    #     cur.execute("""CREATE TABLE IF NOT EXISTS words (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     word_en TEXT NOT NULL,
    #     word_ru TEXT NOT NULL
    #     )""")
    bot.send_message(message.chat.id, f"Привет, {message.chat.first_name}!")

@bot.message_handler(commands=["del"]) # удаление слова из БД
def deletion_word(message):
    markap = types.InlineKeyboardMarkup()

    if adminRule == True:
        with sq.connect("dictionary.db") as con:
            cur = con.cursor()

            cur.execute("SELECT word_en, word_ru FROM words")
            for result in cur:
                markap.add(types.InlineKeyboardButton(f"{result[0]} - {result[1]}", callback_data=f"{result[0]}"))
            bot.send_message(message.chat.id, "Выберите, какую тему вы хотите удалить:", reply_markup=markap)
    else:
        bot.send_message(message.chat.id, "У вас нет прав доступа!")

@bot.callback_query_handler(func=lambda callback: True) # удаление темы из БД
def callback_message(callback):
    with sq.connect("dictionary.db") as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM words WHERE word_en='{callback.data}'")

        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Удаление завершено")

@bot.message_handler(commands=["add"]) # добавление нового слова в БД
def add(message):
    if adminRule == True:
        bot.send_message(message.chat.id, "Сначала введите слово на английском, а потом, через диффис, на русском (прим. train - поезд)")
        bot.register_next_step_handler(message, add_word)
    else:
        bot.send_message(message.chat.id, "У вас нет прав доступа!")

def add_word(message):
    with sq.connect("dictionary.db") as con:
        cur = con.cursor()
        str = message.text.split("-")
        cur.execute(f"INSERT INTO words (word_en, word_ru) VALUES ('{str[0]}', '{str[1]}')")

    bot.send_message(message.chat.id, "Слова добавлены")

@bot.message_handler(commands=["print"]) # выводит в чат список слов
def print_words_list(message):
    list_words = "Список слов:\n"
    with sq.connect("dictionary.db") as con:
        cur = con.cursor()

        cur.execute("SELECT word_en, word_ru FROM words")
        for result in cur:
            list_words = list_words + f"{result[0]} - {result[1]}\n"

        bot.send_message(message.chat.id, list_words)

@bot.message_handler(commands=["admin"]) # проверка пароля для входа под админом
def admin_enter(message):
    bot.send_message(message.chat.id, "Введите пароль для входа под администратором.")
    bot.register_next_step_handler(message, check_pass)

def check_pass(message):
    global adminRule # чтобы изменить глобальную переменную
    if message.text == "1234":
        adminRule = True
        bot.send_message(message.chat.id, "Вы вошли под администраторм.")
    else:
        bot.send_message(message.chat.id, "Пароль неверный!")

bot.polling(none_stop=True)