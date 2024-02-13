import io
import requests
import telebot
import asyncio
import pandas as pd
from Stages import User_Stage
from User import User, Interaction_DB, connect_to_DB
from config import config
from PIL import Image
from Class_keyboard import Keyboard
from telebot import types
from flask import Flask, request
from sqlalchemy.orm import sessionmaker
import datetime, threading, time
bot = telebot.TeleBot(config.token)


users = pd.DataFrame(columns=['user_id', 'user_stage'])
dict_of_questions = {
    0: 'У вас гражданство РФ',
    1: 'ВЫ живете в Москве'
}

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.id == session.return_user_by_id(message.chat.id).id:
        session.replace_user_stage(message.chat.id, User_Stage.admin_mod)
        keyboard = Keyboard()
        keyboard.add_button('Выйти из режима', 'exit')
        keyboard.add_button('Получить базу данных', 'get_data')
        bot.send_message(message.chat.id,
                         f'Вы в режиме админа',
                         reply_markup=keyboard.get_keyboard()
                         )

@bot.callback_query_handler(func= lambda call: call.data in ['exit', 'get_data'])
def callback_for_admin_(call):
    if session.check_user_stage(call.message.chat.id) == User_Stage.admin_mod:
        if call.data == 'exit':
            bot.send_message(call.message.chat.id,
                             f'Вы в обычном режиме, напишите /start'
                             )
            session.replace_user_stage(call.message.chat.id, User_Stage.start_stage)
        elif call.data == 'get_data':
            bot.send_message(call.message.chat.id,
                             f'Отправляю вам резервные данные'
                             )
            send_bd(call.message.chat.id)

def send_bd(call_id):
    file = open('./sqlite3.db')
    bot.send_document(call_id, file)

def send_remind(call_id):
    bot.send_message(call_id,
                     f'У вас есть непройденный тест')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True);
    if session.check_user_stage(message.chat.id) != User_Stage.start_stage:
        stage = session.return_user_by_id(message.chat.id).get_stage()
        if stage == User_Stage.answer_question:
            keyboard = Keyboard()
            keyboard.add_button('да', 'continue')
            keyboard.add_button('нет', 'break')
            bot.send_message(message.chat.id,
                             f'У вас есть непройденный тест, продолжите отвечать на впопросы?',
                             reply_markup=keyboard.get_keyboard()
                             )

    answer = f'Здравствуйте, готовы ли вы начать'
    if session.check_user_id(message.chat.id) == False:
        session.add_new_user(message.chat.id, User_Stage.start_stage)
    bot.send_message(message.chat.id, answer, reply_markup=markup);

@bot.message_handler(func= lambda message: message)

@bot.message_handler(content_types=['text'])
def get_start_answer(message):
    if session.check_user_stage(message.chat.id, User_Stage.start_stage):
        if message.text.lower() == 'да':
            keyboard = Keyboard()
            keyboard.add_button('да', 'continue')
            keyboard.add_button('нет', 'break')
            bot.send_message(message.chat.id,
                             f'Сейчас я задам вам несколько вопросов по поводу вакансии\n Вы готовы?',
                             reply_markup=keyboard.get_keyboard()
                             )
            session.replace_user_stage(message.chat.id, User_Stage.answer_question)

        else:
            bot.send_message(message.chat.id,
                             f'Я вас не понимаю, напишите команду Help или снова перейдите по ссылке',
                             )
    else:
        if session.check_user_stage(message.chat.id, User_Stage.wait_salary):
            try:
                text = int(message.text)
                session.replace_user_stage(message.chat.id, User_Stage.finally_stage)
                session.add_salary(message.chat.id, text)
                keyboard = Keyboard()
                keyboard.add_button('да', 'New_start')
                keyboard.add_button('нет', 'Finish')
                bot.send_message(message.chat.id,
                                 f'Ответы записаны, ожидайте HR. Он скоро вам напишет. Желаете пройти тест заного?',
                                 reply_markup=keyboard.get_keyboard()
                                 )
            except:
                bot.send_message(message.chat.id,
                                 f'Напишите зарплату числом\n Например: 70000')
                ask_next_question(message.chat.id)
        elif session.check_user_stage(message.chat.id, User_Stage.finally_stage):
            keyboard = Keyboard()
            keyboard.add_button('да', 'New_start')
            keyboard.add_button('нет', 'Finish')
            bot.send_message(message.chat.id,
                             f'Ответы записаны, ожидайте HR. Он скоро вам напишет. Желаете пройти тест заного?',
                             reply_markup=keyboard.get_keyboard()
                             )

@bot.callback_query_handler(func= lambda call: call.data in ['continue', 'break', 'New_start', 'Finish'])
def callback_from_start_stage(call):
    if session.check_user_stage(call.message.chat.id, User_Stage.answer_question):
        if call.data == 'continue':
            session.replace_user_stage(call.message.chat.id, User_Stage.answer_question)
            # try:
            #     session.set_some_questions(dict_of_questions)
            # except:
            #     print('')
            ask_next_question(call.message.chat.id)
        elif call.data == 'break':
            session.replace_user_stage(call.message.chat.id, User_Stage.start_stage)
            session.delete_user_answers(call.message.chat.id)
            bot.send_message(call.message.chat.id,
                             f'Хорошо, напишите "/start" как будете готовы',
                             )

    elif call.data == 'New_start':
        session.replace_user_stage(call.message.chat.id, User_Stage.start_stage)
        session.delete_user_answers(call.message.chat.id)
        bot.send_message(call.message.chat.id,
                         f'Хорошо, напишите "/start" как будете готовы',
                         )
    elif call.data == 'Finish':
        bot.send_message(call.message.chat.id,
                         f'Хорошо, ждите ответа HR',
                         )


def ask_next_question(chat_id):
    if session.get_answer_count(chat_id) < len(dict_of_questions):
        question_index = session.get_answer_count(chat_id)
        question = dict_of_questions[question_index]
        keyboard = Keyboard()
        keyboard.add_button('да', 'answer_yes'+f'{question_index}')
        keyboard.add_button('нет', 'answer_no'+f'{question_index}')
        bot.send_message(chat_id, f'{question}d', reply_markup=keyboard.get_keyboard())
    else:
        bot.send_message(chat_id, f'Какие у вас зарплатные ожидания')
        session.replace_user_stage(chat_id, User_Stage.wait_salary)


@bot.callback_query_handler(func=lambda call: 'answer_yes' in call.data or 'answer_no' in call.data)
def handle_answer(call):
    if 'answer_yes' in call.data:
        session.add_answer(call.message.chat.id, 'yes', session.get_question_by_id(int(call.data[10:])))
    elif 'answer_no' in call.data:
        session.add_answer(call.message.chat.id, 'no', session.get_question_by_id(int(call.data[9:])))
    ask_next_question(call.message.chat.id)





# @app.route('/webhook', methods=['POST'])
# def webhook():
#     if request.headers.get('content-type') == 'application/json':
#         json_string = request.get_data().decode('utf-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return '', 200
#     else:
#         return '', 403

def send_reserve():
    global next_call
    next_call = next_call + 86400
    threading.Timer(next_call - time.time(), send_reserve).start()
    send_bd(523223092)

async def main():

    engine = connect_to_DB()
    Session = sessionmaker(bind=engine)
    global session
    session = Interaction_DB(Session())
    send_reserve()
    while True:
        try:
            await bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())

