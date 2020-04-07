# coding=utf-8
import header
import telebot
import pymysql
import sys
import time
import datetime
import os
import urllib


reload(sys)
sys.setdefaultencoding('utf8')

bot = telebot.TeleBot(header.token)
bot.remove_webhook()

def addUser(message): #  Новый пользователь
    friend_id = message.text.replace("/start ", "")
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    if not cur.execute("SELECT * FROM users WHERE id = %s", (message.from_user.id,)):
        name = ""
        if message.chat.first_name:
            name += str(message.chat.first_name)
        if message.chat.last_name:
            name += " " + str(message.chat.last_name)
        if message.from_user.username:
            name += " (@" + str(message.from_user.username) + ")"

        if friend_id.isdigit():
            bot.send_message(chat_id=friend_id, text="Вам начислено 15р за приглашенного друга.️", parse_mode="HTML")
            bot.send_message(chat_id=message.chat.id,
                             text="Вам начислено 15р за переход по партнерской ссылке. Приглашайте других пользователей и получайте по 15р за каждого человека!",
                             parse_mode="HTML")
            cur.execute("INSERT INTO users (id,name, balance) VALUES(%s, %s, 15) ", (message.chat.id, name))
            cur.execute("UPDATE users SET balance = balance + 15, addUsers = addUsers + 1 WHERE id = %s", (friend_id))
        else:
            cur.execute("INSERT INTO users (id,name) VALUES(%s, %s) ", (message.chat.id, name))
    con.commit()
    con.close()


def checkUser(message): # Проверить, есть ли пользователь в базе
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db)
    cur = con.cursor()
    user = cur.execute("SELECT * FROM users WHERE id = %s", (message.from_user.id,))
    con.commit()
    con.close()
    if user:
        return True
    else:
        return False

def getBalance(userID):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT balance FROM users WHERE id = %s ", (userID))
    con.commit()
    con.close()
    return cur.fetchone()[0]

def setBalance(userID):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET balance = 0 WHERE id = %s ", (userID))
    con.commit()
    con.close()

def addToField(userID, field, col):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db,charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET " + field + " = " + field + "+ %s WHERE id = %s ", (col,userID))
    con.commit()
    con.close()

def addCommand(id, command):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET command = %s WHERE id = %s ", (command, id))
    con.commit()
    con.close()

def getField(message, field):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT " + field + " FROM users WHERE id = %s ", (message.chat.id,))
    con.commit()
    con.close()
    return cur.fetchone()[0]


def clearDB(message):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET command = NULL, text=NULL WHERE id = %s ", (message.chat.id))
    con.commit()
    con.close()



def tg_chanels(message, msg_id):
    lastChannel = getField(message, "tg")
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT * FROM chanels WHERE id > %s", (lastChannel,))
    chanel = cur.fetchone()
    if chanel == None:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id, text="Вы выполнили все задания, скоро будут новые!")
    else:
        cur.execute("UPDATE users SET tg = %s WHERE id = %s", (chanel[0],message.chat.id))
        bot.edit_message_text(chat_id=message.chat.id,message_id=msg_id, text="Задание № " +str(chanel[0])+ "\n1️⃣ Перейдите на канал, подпишитесь и пролистайте ленту вверх (5-10 постов)\n"
                                                       "2️⃣ Возвращайтесь в бота за вознаграждением!", parse_mode="markdown", reply_markup=keyFollow(bot.export_chat_invite_link(chanel[1])))
    con.commit()
    con.close()

def checkChanel(message,callid):
    num = [int(s) for s in message.text.split() if s.isdigit()]
    num = num[0]
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT * FROM chanels WHERE id = %s", (num,))
    cid = cur.fetchone()[1]
    status = bot.get_chat_member(chat_id=cid, user_id=message.chat.id).status
    if status != "member" and status != "administrator" and status != "creator":
        bot.answer_callback_query(callback_query_id=callid, text="Вы не подписаны на канал!", show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=callid, text="Начисяем вознаграждение!")
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Вам начислено 15р за подписку на канал\n\n*В случае отписки мы оштрфуем вас на 50р*", reply_markup=keyNext(), parse_mode="markdown")
        addToField(message.chat.id, "balance", 15)
    con.commit()
    con.close()

def setDate(userID):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db,charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET active = %s WHERE id = %s ", (datetime.date.today(), userID))
    con.commit()
    con.close()

def people_count():
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db)
    cur = con.cursor()
    cur.execute("select count(*) from users");
    people = cur.fetchone()[0]
    con.commit()
    con.close()
    if(people):
        return people
    else:
        return 0

def addChanel(id):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db)
    cur = con.cursor()
    cur.execute("INSERT INTO chanels (idc) VALUES(%s) ", (id))
    con.commit()
    con.close()

def getCh(userID):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT * FROM chanels ")
    chanels = cur.fetchall()
    kboard = keyDel()
    for ch in chanels:
        chat = bot.get_chat(chat_id=ch[1])
        txt = "ID Канала в БД - " + str(ch[0]) + "\n"\
              "ID Канала в TG " + str(ch[1]) + "\n"\
              "Название канала - " + chat.title + "\n"\
              "Ссылка на канал - " + chat.invite_link
        bot.send_message(userID, txt, reply_markup=kboard)
        time.sleep(.2)
    con.commit()
    con.close()

def delCh(cid, message):
    num = [int(s) for s in message.text.split() if s.isdigit()]
    num = num[0]
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    bot.delete_message(message.chat.id, message.message_id)
    bot.answer_callback_query(callback_query_id=cid, text="Канал удален", show_alert=True)
    cur.execute("DELETE FROM chanels WHERE id = %s", (num))
    con.commit()
    con.close()

def addText(message):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET text = %s WHERE id = %s", (message.text, int(message.chat.id)))
    con.commit()
    con.close()

def getText(message):
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT text FROM users WHERE id = %s", (message.chat.id))
    message_text = cur.fetchone()[0]
    con.commit()
    con.close()
    return message_text

#Клавиатуры

def keyStart(): # /start
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row("/start")
    return user_markup

def keySoc():
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row(header.b_tg, header.b_inst)
    user_markup.row(header.b_home)
    return user_markup

def keyDel():
    user_markup = telebot.types.InlineKeyboardMarkup()
    user_markup.add(telebot.types.InlineKeyboardButton(text="Удалить канал", callback_data=header.b_del))
    return user_markup

def keyFollow(link):
    user_markup = telebot.types.InlineKeyboardMarkup()
    user_markup.add(telebot.types.InlineKeyboardButton(text="Подписаться ⤴️", url=link))
    user_markup.add(telebot.types.InlineKeyboardButton(text="Проверить подписку 🔄", callback_data=header.b_check))
    return user_markup

def keyNext():
    user_markup = telebot.types.InlineKeyboardMarkup()
    user_markup.add(telebot.types.InlineKeyboardButton(text="Следующее задание ➡️", callback_data=header.b_next))
    return user_markup

def keyPartner():
    user_markup = telebot.types.InlineKeyboardMarkup()
    user_markup.add(telebot.types.InlineKeyboardButton(text="Бонус 🎁", url="http://rotenberg.beget.tech/track/1/source/campaign-ads"))
    return user_markup

def keyAdmin():
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row(header.b_msg, header.b_ppl_count)
    user_markup.row(header.b_addch, header.b_delch)
    user_markup.row(header.b_home)
    return user_markup

def keyMain(message):
    clearDB(message)
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row(header.b_earn, header.b_balance)
    user_markup.row(header.b_more, header.b_partner)
    if message.chat.id in header.admin:
        user_markup.row(header.b_admin)
    return user_markup

def keyBalance():
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row(header.b_ya, header.b_card)
    user_markup.row(header.b_home)
    return user_markup

def sendMessage():
    user_markup = telebot.types.InlineKeyboardMarkup()
    btn_send_all = telebot.types.InlineKeyboardButton(text=header.b_send_all, callback_data=header.b_send_all)
    btn_cancel = telebot.types.InlineKeyboardButton(text=header.b_cancel, callback_data=header.b_cancel)
    user_markup.add(btn_send_all)
    user_markup.add(btn_cancel)
    return user_markup

def keyYaPay(message):
    user_markup = telebot.types.InlineKeyboardMarkup()
    user_markup.add(telebot.types.InlineKeyboardButton(text='Оплатить 100р 💳 Картой', url='https://money.yandex.ru/quickpay/confirm.xml?receiver=410016025009437&quickpay-form=shop&targets=' + urllib.quote_plus('Подтверждение реквизитов')+ '&paymentType=AC&sum=100&label=' + str(message.chat.id)))
    user_markup.add(telebot.types.InlineKeyboardButton(text='Оплатить 100р 📒 Я.Деньгами',url='https://money.yandex.ru/quickpay/confirm.xml?receiver=410016025009437&quickpay-form=shop&targets=' + urllib.quote_plus('Подтверждение реквизитов') + '&paymentType=PC&sum=100&label=' + str(message.chat.id)))
    return user_markup


@bot.callback_query_handler(func = lambda c: True)
def inline(c):
    if c.data == header.b_check:
        checkChanel(c.message,c.id)
    elif c.data == header.b_next:
        tg_chanels(c.message, c.message.message_id)
    elif c.data == header.b_del:
        delCh(c.id, c.message)
    if c.data == header.b_cancel:
        clearDB(c.message)
        bot.answer_callback_query(callback_query_id=c.id, text="Отправка отменена")
        bot.delete_message(chat_id=c.message.chat.id, message_id=c.message.message_id)
    elif c.data == header.b_send_all:
        bot.answer_callback_query(callback_query_id=c.id, text="Начинаем расылку")
        os.system("nohup /usr/bin/python /bots/clientBots/moneyernbot/message.py " + str(c.message.chat.id) + "  >/dev/null &")

@bot.message_handler(commands=['start'])
def botStart(message):
    addUser(message)
    bot.send_message(chat_id=message.from_user.id, text=header.t_hello,reply_markup=keyMain(message), parse_mode="HTML")

@bot.message_handler(content_types=["audio", "document", "photo", "sticker", "video", "video_note", "location"]) #Больше не трогаем
def msg(message):
    lastCommand = getField(message, "command")
    if lastCommand == header.b_addch:
        if message.forward_from_chat:
            try:
                bot.export_chat_invite_link(message.forward_from_chat.id)
            except:
                bot.send_message(message.chat.id,
                                 text="Ошибка! Боту не разрешено приглашать новых пользователей, обратитесь к создаелю канала, чтобы тот предоставил соответсвующие права боту.",
                                 parse_mode="markdown")
            else:
                addChanel(message.forward_from_chat.id)
                bot.send_message(message.chat.id,
                                 text="Канал успешно добавлен, подробная информаия о канале находится в разделе \"" + header.b_delch + "\"",
                                 parse_mode="markdown")
                clearDB(message)

@bot.message_handler(content_types=['text'])
def answr(message):
    if checkUser(message):
        if message.text == header.b_earn:
            bot.send_message(chat_id=message.chat.id, text=header.t_soc, reply_markup=keySoc(), parse_mode="markdown")
        elif message.text == header.b_inst: # instagram
            if getField(message, "active") != datetime.date.today():
                setDate(message.chat.id)
                os.system("nohup /usr/bin/python /bots/clientBots/moneyernbot/video.py " + str(message.chat.id) + "  >/dev/null &")
            else:
                bot.send_message(chat_id=message.from_user.id,text="Услугой можно пользоваться только 1 раз за сутки.", parse_mode="markdown")
        elif message.text == header.b_tg: # instagram
            tg_chanels(message, bot.send_message(chat_id=message.chat.id, text="Поиск заданий...").message_id)
        elif message.text == header.b_balance: # Вывод
            bot.send_message(chat_id=message.from_user.id, text="*Баланс:* " + str(getBalance(message.chat.id)) + "р.\n" + header.t_out, reply_markup=keyBalance(),
                             parse_mode="markdown")
        elif message.text == header.b_more:
            bot.send_message(chat_id=message.chat.id, text="Переходи по ссылке и получай бонус до *75.000р!*", reply_markup=keyPartner(), parse_mode="markdown")
        elif message.text == header.b_home: # Назад
            clearDB(message)
            bot.send_message(chat_id=message.chat.id, text=header.t_main, reply_markup=keyMain(message))
        elif message.text == header.b_admin:
            bot.send_message(chat_id=message.chat.id, text="Управление ботом 🤖", reply_markup=keyAdmin())
        elif message.text == header.b_partner:
            bot.send_message(chat_id=message.from_user.id,text=header.t_partner + "https://tele.click/MoneyErnBot?start=" + str(message.from_user.id) + "\n\nПриглашено пользователей: " + str(getField(message, "addUsers")),parse_mode="markdown", disable_web_page_preview=True)
        elif message.text == header.b_msg:
            addCommand(message.from_user.id, message.text)
            bot.send_message(message.from_user.id, "Введите текст сообщения. Бот поддерживает разметку *markdown*", parse_mode="markdown")
        elif message.text == header.b_phone or message.text == header.b_qiwi or message.text == header.b_ya or message.text == header.b_card: # Вывод на кошелек
            if getBalance(message.chat.id) > 0:
                addCommand(message.chat.id, message.text)
                txt = ""
                if message.text == header.b_phone:
                    txt = "Укажите номер телефона, на который придет выплата"
                elif message.text == header.b_qiwi:
                    txt = "Укажите номер Qiwi кошелька, на который придет выплата"
                elif message.text == header.b_ya:
                    txt = "Укажите номер Яндекс кошелька, на который придет выплата"
                elif message.text == header.b_card:
                    txt = "Укажите номер банковской карты, на которую придет выплата"
                bot.send_message(chat_id=message.chat.id, text=txt, reply_markup=keyBalance())
            else:
                bot.send_message(chat_id=message.chat.id, text=header.t_berror, reply_markup=keyMain(message), parse_mode="markdown")
        else:
            lastCommand = getField(message, "command")
            if lastCommand == header.b_msg:  # Ввод сообщения
                addText(message)
                mytext = getText(message)
                try:
                    bot.send_message(message.chat.id, text=mytext, reply_markup=sendMessage(), parse_mode="markdown",disable_web_page_preview=True)
                except:
                    bot.send_message(message.chat.id, "Где-то ошибка, проверь разметку")
            elif lastCommand == header.b_phone or lastCommand == header.b_qiwi or lastCommand == header.b_card or lastCommand == header.b_ya:
                allok = False
                if lastCommand == header.b_phone:
                    if message.text.isdigit():
                        if len(message.text) > 10:
                            allok = True
                        else:
                            bot.send_message(message.from_user.id, 'Номер должен содержать от 11 цифр')
                            return
                    else:
                        bot.send_message(message.from_user.id, 'Номер телефона должен состоять только из цифр.\n------\nПример: 79897773322')
                elif lastCommand == header.b_qiwi:
                    if message.text.isdigit():
                        if len(message.text) > 10:
                            allok = True
                        else:
                            bot.send_message(message.from_user.id, 'Номер Qiwi кошелька должен содержать от 11 цифр')
                            return
                    else:
                        bot.send_message(message.from_user.id, 'Номер Qiwi кошелька должен состоять только из цифр.\n------\nПример: 79897773322')
                elif lastCommand == header.b_card:
                    if message.text.isdigit():
                        if len(message.text) == 16:
                            allok = True
                        else:
                            bot.send_message(message.from_user.id, 'Номер карты должен содержать 16 цифр')
                            return
                    else:
                        bot.send_message(message.from_user.id,'Номер карты должен состоять только из цифр.\n------\nПример: 1111222233334444')

                elif lastCommand == header.b_ya:
                    if message.text.isdigit():
                        if len(message.text) == 15:
                            allok = True
                        else:
                            bot.send_message(message.from_user.id, 'Номер Яндекс кошелька должен содержать 15 цифр')
                            return
                    else:
                        bot.send_message(message.from_user.id,'Номер Яндекс кошелька должен состоять только из цифр.\n------\nПример: 111122223333444')
                if allok:
                    bot.send_message(message.chat.id, text = "Все Окей! Ожидайте перевода.",parse_mode="markdown")
                    setBalance(message.chat.id)
                    clearDB(message)
                    if getField(message, "profile") == 0:
                        time.sleep(2)
                        bot.send_message(message.chat.id, text="Ошибка, наша платежная система не может зачислить деньги, пожалуйста подтвердите свои реквизиты:\n\n1) Отправьте нам 100р тем кошельком/картой, на который/которую планируете выводить средства"
                                                               "\n\n2) После подтверждения резвизитов мы сможем моментально перечислять Вам деньги"
                                                               "\n\n3) Данная сумма будет начислена на аккаунт и в дальнейшем может быть выведена", reply_markup=keyYaPay(message),parse_mode="HTML")
            elif lastCommand == header.b_addch:
                if message.forward_from_chat:
                    try:
                        bot.export_chat_invite_link(message.forward_from_chat.id)
                    except:
                        bot.send_message(message.chat.id, text="Ошибка! Боту не разрешено приглашать новых пользователей, обратитесь к создаелю канала, чтобы тот предоставил соответсвующие права боту.",parse_mode="markdown")
                    else:
                        addChanel(message.forward_from_chat.id)
                        bot.send_message(message.chat.id, text="Канал успешно добавлен, подробная информаия о канале находится в разделе \"" + header.b_delch + "\"", parse_mode="markdown")
                        clearDB(message)
                else:
                    bot.send_message(message.chat.id, text="Сообщение переслано не из канала", parse_mode="markdown")
            elif message.chat.id in header.admin:
                if message.text == header.b_ppl_count:
                    bot.send_message(message.from_user.id, "Людей в боте: <b>" + str(people_count()) + "</b>",parse_mode="HTML")
                elif message.text == header.b_addch:
                    addCommand(message.from_user.id, message.text)
                    bot.send_message(message.from_user.id, header.t_addch, parse_mode="markdown")
                elif message.text == header.b_delch:
                    getCh(message.chat.id)
                elif message.text == header.b_msg:
                    ""
            else:
                clearDB(message)
                bot.send_message(message.chat.id, text="Для управления ботом используйте кнопки клавиатуры", reply_markup=keyMain(message), parse_mode="markdown")

    else:
        bot.send_message(chat_id=message.from_user.id, text="Нажмите /start", reply_markup=keyStart(),
                         parse_mode="HTML")


bot.polling(none_stop=True, timeout=60)