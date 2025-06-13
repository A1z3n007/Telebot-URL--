import telebot
import requests

from types import SimpleNamespace

TOKEN = "YOU_API_TOKEN"
bot = telebot.TeleBot(TOKEN)
whitelist = ["TELEGRAM_ID_1", "TELEGRAM_ID_2"]

def bool_1(message):
    return str(message.chat.id) in whitelist

def welcome(message):
    user_id = str(message.chat.id)
    if user_id in whitelist:
        bot.send_message(message.chat.id, "✅ Добро пожаловать в бота!")
        return True
    else:
        bot.send_message(message.chat.id, "❌ У вас нет доступа к этому боту.")
        return False

def process_article(message):
    art = message.text.strip()
    base_url = f"https://alm-basket-cdn-02.geobasket.ru/vol{art[0:4]}/part{art[0:6]}/{art}"

    info_url = f"{base_url}/info/ru/card.json"
    response = requests.get(info_url)
    if response.status_code == 200:
        data = response.json()
        bot.send_message(message.chat.id, f"📦 {data.get('imt_name', 'Название недоступно')}")
        bot.send_message(message.chat.id, f"🔢 Артикул: {data.get('imt_id', 'Артикул недоступен')}")
        bot.send_message(message.chat.id, f"🎨 Цвет: {data.get('nm_colors_names', 'Цвет недоступен')}")
        bot.send_message(message.chat.id, f"📝 Описание: {data.get('description', 'Описание недоступно')}")
        bot.send_message(message.chat.id, f"📂 Тип: {data.get('subj_name', 'Тип недоступен')}")
        bot.send_message(message.chat.id, f"🏷 Бренд: {data.get('selling', {}).get('brand_name', 'Бренд недоступен')}")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось получить информацию о товаре.")
        return

    price_url = f"{base_url}/info/price-history.json"
    response_2 = requests.get(price_url)
    if response_2.status_code == 200:
        data_2 = response_2.json()
        prices = []
        for item in data_2:
            try:
                rub_price = item["price"]["RUB"] // 100
                tg_price = rub_price * 6.4
                prices.append(round(tg_price))
            except (KeyError, TypeError):
                continue

        if prices:
            current_price = prices[-1]
            avg_price = sum(prices) / len(prices)
            if current_price < avg_price:
                level = "Цена ниже средней"
            elif current_price > avg_price:
                level = "Цена выше средней"
            else:
                level = "Цена равна средней"
            bot.send_message(message.chat.id, (
                f"💰 Средняя цена: {round(avg_price)}₸\n"
                f"💸 Текущая цена: {current_price}₸\n"
                f"📉 Уровень цены: {level}"
            ))
        else:
            bot.send_message(message.chat.id, "⚠ История цен пуста или в неверном формате.")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось получить историю цен.")

    # --- Получение рейтинга и количества отзывов ---
    details_url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=kzt&dest=269&spp=30&hide_dtype=10%3B13%3B14&ab_testing=false&lang=ru&nm={art}"
    response_3 = requests.get(details_url)

    if response_3.status_code == 200:
        try:
            json_data = response_3.json()
            product = json_data['data']['products'][0]

            rating = product.get('reviewRating', 'N/A')
            feedbacks = product.get('feedbacks', 'N/A')

            bot.send_message(message.chat.id, f"📊 Рейтинг товара: {rating} ⭐️\n💬 Отзывов: {feedbacks}")
        except Exception as e:
            print("Rating parse error:", e)
            bot.send_message(message.chat.id, "⚠️ Не удалось извлечь рейтинг или отзывы.")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось получить рейтинг товара.")

    # --- Получение отзывов ---
    reviews_url = f"https://feedbacks1.wb.ru/feedbacks/v1/{art}?limit=3&skip=0"
    response_4 = requests.get(reviews_url)

    if response_4.status_code == 200:
        try:
            data_4 = response_4.json()
            reviews = data_4.get("feedbacks", [])
            if reviews:
                review_msgs = ["🗣 Отзывы покупателей:"]
                for review in reviews:
                    text = review.get("text", "")
                    stars = review.get("productValuation", "")
                    review_msgs.append(f"⭐ {stars} — {text[:120]}...")
                bot.send_message(message.chat.id, "\n\n".join(review_msgs))
            else:
                bot.send_message(message.chat.id, "Отзывы отсутствуют.")
        except Exception as e:
            print("Отзывы парсинг ошибка:", e)
            bot.send_message(message.chat.id, "Не удалось получить отзывы.")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось подключиться к сервису отзывов.")


@bot.message_handler(commands=['start'])
def start(message):
    welcome(message)

@bot.message_handler(content_types=['text'])
def on_text(message):
    if str(message.chat.id) in whitelist:
        process_article(message)
    else:
        welcome(message)

if __name__ == "__main__":
    bot.infinity_polling()
