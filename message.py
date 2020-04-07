# coding=utf-8
import sys
import header
import telebot
import pymysql


bot = telebot.TeleBot(header.token)
userID = sys.argv[1]

def clearDB():
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("UPDATE users SET command = NULL, text=NULL WHERE id = %s ", (userID))
    con.commit()
    con.close()

def getIDS():
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT id FROM users")
    usrsIDS = cur.fetchall()
    con.commit()
    con.close()
    return usrsIDS

def getText():
    con = pymysql.connect(host=header.host, user=header.usr, passwd=header.password, db=header.db, charset="utf8mb4")
    cur = con.cursor()
    cur.execute("SELECT text FROM users WHERE id = %s", (userID))
    message_text = cur.fetchone()[0]
    con.commit()
    con.close()
    return message_text

usrIDS = getIDS()
numOfIDS = len(usrIDS)
myText = getText()
clearDB()
currenrUsr = 0  # Текущий юзер
j = 0  # Успешно отправлено
msg_id = bot.send_message(chat_id=userID, text="Отправлено 1 из " + str(numOfIDS), parse_mode="markdown").message_id
for usrID in usrIDS:
    currenrUsr += 1
    if currenrUsr % 20 == 0:
        bot.edit_message_text(chat_id=userID, message_id=msg_id, text="Отправлено " + str((currenrUsr)) + " из " + str(numOfIDS))
    try:
        bot.send_message(chat_id=usrID[0], text=myText, parse_mode="markdown", disable_web_page_preview=True)
    except:
        j+=1
bot.delete_message(chat_id=userID, message_id=msg_id)
bot.send_message(chat_id=userID, text = "Рассылка завершена.\nОтправлено сообщений: <b>" + str(numOfIDS - j) + "</b> из <b>" + str(numOfIDS) + "</b>", parse_mode="HTML")