# Telegram bot that can make an appointment to a barbershop

from telegram import *
from telegram.ext import *
from requests import *
import functions
import asyncio
from pyppeteer import launch
import threading
from threading import Thread
from queue import Queue
from PIL import Image
import io

updater = Updater(token="5249487701:AAH0M62sDa5df6CuGYBsBfpNJCrNKl3jXCY")
dispatcher = updater.dispatcher

welcome_button_yes = "Да, запиши меня! 😎"
welcome_button_no = "Нет, я запишусь потом! 🥸"
greetings_text = "Похоже, пора подстричься! Могу записать тебя к барберу в DANDY"
farewell_text = "Ок, в следующий раз!"
barber_search = "Ищу доступных барберов..."
barber_choose = "Выберите любимого барбера 💇🏽‍♂️️"
service_search = "Ищу доступные услуги..."
service_choose = "Выберите услугу ✂️  🪒 🚿"
dates_search = "Ищу доступные даты для записи..."
date_choose = "Выберите удобную Вам дату 🗓"
times_search = "Ищу доступные слоты по времени..."
time_choose = "Выберите удобное время для визита 🕔"
approval_search = "Фомирую детали Вашей брони..."
approve_caption = "Детали заказа"
approve_params = "Оформить визит?"
phone_number = "Отлично! Осталось ввести номер телефона (10 цифр, которые после +7)"
final_caption = "Вы записаны, ждем Вас с нетерпением!"


def startCommand(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton(text=welcome_button_yes, callback_data=welcome_button_yes)],
               [InlineKeyboardButton(text=welcome_button_no, callback_data=welcome_button_no)]]

    context.bot.send_message(chat_id=update.effective_chat.id, text=greetings_text,
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


def queryHandler(update: Update, context: CallbackContext):
    query = update.callback_query.data
    update.callback_query.answer()
    step, pick, barber_id = functions.query_parsed(query)
    print(step, pick, barber_id)

    if welcome_button_no in query:
        context.bot.send_message(chat_id=update.effective_chat.id, text=farewell_text)

    # chose an employees
    if welcome_button_yes in query:
        context.bot.send_message(chat_id=update.effective_chat.id, text=barber_search)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        barbers_names, barbers_ids = new_loop.run_until_complete(functions.barbers_list())
        context.bot.send_message(chat_id=update.effective_chat.id, text=barber_choose,
                                 reply_markup=functions.get_buttons_barbers(barbers_names, barbers_ids))

    if step == "barber_button_pushed":
        context.bot.send_message(chat_id=update.effective_chat.id, text=service_search)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        services_list, url_for_barber_id = new_loop.run_until_complete(functions.services_list(int(pick)))
        barber_id = url_for_barber_id.split("/")[3].split("=")[1]
        context.bot.send_message(chat_id=update.effective_chat.id, text=service_choose,
                                 reply_markup=functions.get_buttons_services(services_list, barber_id=barber_id))

    if step == "service_button_pushed":
        context.bot.send_message(chat_id=update.effective_chat.id, text=dates_search)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        dates_list, url_for_barber_id = new_loop.run_until_complete(functions.dates_list(int(pick), barber_id))
        barber_and_service = url_for_barber_id.split("/")[3].split("=")[1].split('s')
        barber_id = barber_and_service[0]
        service_id = "s" + barber_and_service[1]
        context.bot.send_message(chat_id=update.effective_chat.id, text=date_choose,
                                 reply_markup=functions.get_buttons_dates(dates_list, barber_id=barber_id, service_id=service_id))

    if step == "date_button_pushed":
        context.bot.send_message(chat_id=update.effective_chat.id, text=times_search)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        times_list, url_for_times = new_loop.run_until_complete(functions.times_list(pick, barber_id))
        url_for_times = url_for_times.split("/")[5]
        context.bot.send_message(chat_id=update.effective_chat.id, text=time_choose,
                                 reply_markup=functions.get_buttons_times(times_list, url_time_choose=url_for_times))

    #if time and everything else is chosen -> get a table for approval
    if step == "time_button_pushed":
        context.bot.send_message(chat_id=update.effective_chat.id, text=approval_search)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        image, url_for_approval = new_loop.run_until_complete(functions.apr(int(pick), barber_id))
        url_for_approval = url_for_approval.split("/")[3].split("?")[1]
        #image = Image.open(io.BytesIO(screenshot))

        context.bot.sendMediaGroup(chat_id=update.effective_chat.id, media=[InputMediaPhoto(image, caption=approve_caption)])
        context.bot.send_message(chat_id=update.effective_chat.id, text=approve_params,
                                 reply_markup=functions.get_buttons_approve(url_for_approval))

    if step == "approve_button_pushed":
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        if pick == "0":  # "Да, все норм"
            context.chat_data['link'] = None
            image, final_url = new_loop.run_until_complete(functions.approve_button_pushed(barber_id))
            print(final_url)
            #context.bot.sendMediaGroup(chat_id=update.effective_chat.id,
            #                           media=[InputMediaPhoto(image, caption=final_url)])
            context.chat_data['link'] = final_url
            print(context.chat_data)
            context.bot.send_message(chat_id=update.effective_chat.id, text=phone_number)

        if pick == "1":  # "Нет" - заново выбираем барбера
            context.bot.send_message(chat_id=update.effective_chat.id, text=barber_search)
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            barbers_names, barbers_ids = new_loop.run_until_complete(functions.barbers_list())
            context.bot.send_message(chat_id=update.effective_chat.id, text=barber_choose,
                                     reply_markup=functions.get_buttons_barbers(barbers_names, barbers_ids))


# telephone number handler
def messageHandler(update: Update, context: CallbackContext):
    if len(update.message.text) != 10:
        context.bot.send_message(chat_id=update.effective_chat.id, text=phone_number)
    # need to think of more validation
    if len(update.message.text) == 10:
        telephone_number = update.message.text
        username = update.effective_chat.username
        url = context.chat_data['link']
        context.chat_data['link'] = None

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        image = new_loop.run_until_complete(functions.zapisatsa(telephone_number, username, url))
        context.bot.sendMediaGroup(chat_id=update.effective_chat.id,
                                   media=[InputMediaPhoto(image, caption=final_caption)])
        print(context.chat_data)


dispatcher.add_handler(CommandHandler("start", startCommand))
dispatcher.add_handler(CallbackQueryHandler(queryHandler))
dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))

updater.start_polling(drop_pending_updates=True)
#updater.idle()



