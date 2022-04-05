import telebot
import requests
import time
from bs4 import BeautifulSoup


token = "token"  # Ваш токен
channel_id = "ID"  # Ваш логин канала


bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['text'])
def commands(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Добрый день. Я умею пересылать свежие новости с сайта vc.ru в телеграм канал, где я добавлен в качестве администртора. \nДля начала работы со мной просто напишите мне слово Старт")
    elif message.text == "Старт":
        bot.send_message(message.from_user.id, "Спасибо. С этого времени я буду отслеживать новые статьи и автоматически отпраавлять в ваш канал!\n\nЧтобы прекртить автоматическую отправку статей "
                                               "просто скажите мне Стоп")
        previous_url = None
        while True:
            post_text = parser(previous_url)
            previous_url = post_text[1]
            if post_text[1] is not None:
                if len(post_text[0]) > 4096:
                    message_splitter(post_text[0])
                else:
                    bot.send_message(channel_id, post_text[0])
                time.sleep(1800)
    elif message.text == "Стоп":
        bot.send_message(message.from_user.id, "Я вас понял. Я больше не буду отправлять статьи в ваш канал. Если захотите меня перезапустить, просто напишите мне снова Старт")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши Старт")


def parser(inner_last_url):
    page = requests.get("https://vc.ru/new")
    soup = BeautifulSoup(page.content, "html.parser")
    post = soup.find("div", class_="feed__item l-island-round")
    new_url = post.find("a", class_="content-header__item content-header-number", href=True)["href"].strip()
    if new_url != inner_last_url:
        page = requests.get(new_url)
        soup = BeautifulSoup(page.content, "html.parser")
        post = soup.find("div", class_='l-entry l-island-bg l-island-round lm-pt-16 l-pt-24 l-pb-30')
        title = post.find("h1", class_="content-title").text.strip() + '\n\n '
        full_text = post.find("div", class_='l-entry__content')
        text = str()
        for text_block in full_text.select('div[class="l-island-a"]'):
            text += text_block.text.strip() + '\n'
        return f"{title}\n\n{text}", new_url
    else:
        return None, new_url


def message_splitter(data):
    msg = data
    sub_msgs = []
    while len(msg):
        split_point = msg[:4096].rfind('\n')
        if split_point != -1:
            sub_msgs.append(msg[:split_point])
            msg = msg[split_point+1:]
        else:
            split_point = msg[:4096].rfind('. ')
            if split_point != -1:
                sub_msgs.append(msg[:split_point+1])
                msg = msg[split_point+2:]
            else:
                sub_msgs.append(msg[:4096])
                msg = msg[4096:]

    for send_msg in sub_msgs[:-1]:
        bot.send_message(channel_id, send_msg)
        time.sleep(1)


bot.polling()
