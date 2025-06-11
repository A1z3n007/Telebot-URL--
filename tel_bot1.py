import telebot
from telebot import types
import requests

token = 'Твой API_КЛЮЧ'
bot = telebot.TeleBot(token)

WHITELIST = [1795671737, 1398771724, 1234567890, 9876543210]

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in WHITELIST:
        bot.send_message(message.chat.id, "Привет! Чем могу помочь?")
    else:
        bot.send_message(message.chat.id, f"Доступ запрещён. Ваш ID: {message.from_user.id}")

@bot.message_handler(commands=['wb'])
def get_wb_info(message):
    if message.from_user.id not in WHITELIST:
        bot.send_message(message.chat.id, "Доступ запрещён.")
        return

    msg = bot.send_message(message.chat.id, "Введите артикул товара Wildberries:")
    bot.register_next_step_handler(msg, process_article)

def process_article(message):
    artic = message.text.strip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': f'https://www.wildberries.ru/catalog/{artic}/detail.aspx'
    }
    url = f'https://basket-10.wbbasket.ru/vol{artic[0:4]}/part{artic[0:6]}/{artic}/info/ru/card.json'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        name = data.get("imt_name", "Нет данных")
        brand = data.get("selling", {}).get("brand_name", "Нет данных")
        price = data.get("priceU", "Нет данных")
        desc = data.get("description", "Нет данных")
        msg = f"Название: {name}\nБренд: {brand}\nЦена: {price}\nОписание: {desc}"
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, f"Не удалось получить данные. Код ответа: {response.status_code}")

@bot.message_handler(func=lambda message: message.from_user.id in WHITELIST)
def handle_message(message):
    if message.text == "Проверить белый список":
        bot.send_message(message.chat.id, "Вы в белом списке, команда принята.")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("Проверить белый список")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

def bool_1(c_id):
  if c_id in WHITELIST:
    return True
  else:
    return False

bot.polling()
