# coding=utf-8
import sys
import header
import telebot
import pymysql
import time
import random

bot = telebot.TeleBot(header.token)

userID = sys.argv[1]

stories=20

def addToField(userID, field, col):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db,charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET " + field + " = " + field + "+ %s WHERE id = %s ", (col,userID))
    con.commit()
    con.close()

msg_id = bot.send_message(chat_id=userID, text="#ПросмотрStories\n<b>Выполнено:</b> 1 из " + str(stories), parse_mode="markdown").message_id

i = 0
sum = 0
while i < stories:
    i += 1
    price = round(random.uniform(0.1, 1),2)
    n = random.randint(20,25)
    sum += price
    txt = "#ПросмотрStories\n" + "<b>Выполнено:</b> " + str(i) + " из " + str(stories) + "\n<b>Доход со Stories:</b> " + str(price) + "р."
    bot.edit_message_text(chat_id=userID, message_id=msg_id, text=txt,parse_mode="HTML")
    time.sleep(.8)

bot.delete_message(chat_id=userID, message_id=msg_id)
bot.send_message(chat_id=userID, text="Просмотр Stories завершен.\nЗаработано: " + str(sum) + "руб.", parse_mode="HTML")
addToField(userID, "balance", sum)

