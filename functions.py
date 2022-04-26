from telegram import *
from telegram.ext import *
from requests import *
import functions
import asyncio
from pyppeteer import launch
import datetime
import locale
from time import strptime
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
import time


async def barbers_list():
    start = time.time()
    barbers_names = []
    barbers_ids = []
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    await page.goto('https://n155779.yclients.com/company:106935/idx:0/master#1', {'waitUntil': 'domcontentloaded'})
    await page.waitForSelector('[class^="y-master-card ng-scope"]')
    barbers = await page.querySelectorAll('[class^="y-master-card ng-scope"]')
    for barber in barbers:
        barber_name = await barber.Jeval('[data-master-name]',
                                         pageFunction='node => node.getAttribute("data-master-name")')
        barber_id = await barber.Jeval('[data-master-id]', pageFunction='node => node.getAttribute("data-master-id")')
        barbers_names.append(barber_name)
        barbers_ids.append(barber_id)

    await browser.close()
    print("barbers execution time ", time.time() - start)
    return barbers_names, barbers_ids


def get_buttons_barbers(barbers_names, barbers_ids):
    kbs = []
    kbs2 = []
    for x in range(len(barbers_names)):
        kbs = kbs + [InlineKeyboardButton(text=barbers_names[x], callback_data=str("barber_button_pushed " + str(x)
                                                                                        + " " + str(barbers_ids[x])))]
    kbs = [element for element in kbs]

    for i in range(len(kbs)):
        if i % 4 != 0:
            pass
        else:
            kbs2 = kbs2 + [kbs[i:i + 4]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kbs2)
    return keyboard


def query_parsed(query):
    return(query.split()[0], query.split()[1], query.split()[2])


async def services_list(pick):
    ### Takes barber button pick and returns services list
    start_time = time.time()
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    await page.goto('https://n155779.yclients.com/company:106935/idx:0/master#1', {'waitUntil': 'domcontentloaded'})
    await page.waitForSelector('h3')
    barbers = await page.querySelectorAll("h3")
    await barbers[pick].click()
    await page.waitFor(700)
    url_for_barber_id = await page.evaluate("() => window.location.href")

    await page.goto('https://n155779.yclients.com/company:106935/idx:0/service#1', {'waitUntil': 'domcontentloaded'})


    await page.waitForSelector('[ng-bind-html^="$ctrl"]')
    services = await page.querySelectorAll('[ng-bind-html^="$ctrl"]')
    services_list = []
    services_ids = []
    for service in services:
        service_name = await service.getProperty("textContent")
        service_name = await service_name.jsonValue()
#### attempt to get services_ids - FAILED
 #       service_id = await service.getProperty("class")
 #       service_id = await service_id.jsonValue()
        services_list.append(service_name)
 #       services_ids.append(service_id)

    await browser.close()
    print("services list time for execution ", (time.time() - start_time))
    return services_list, url_for_barber_id #, services_ids


def get_buttons_services(arr, barber_id):
    kbs = []
    for x in range(len(arr)):
        pick = arr[x]
        print(pick)
        kbs = kbs + [InlineKeyboardButton(text=arr[x], callback_data=str("service_button_pushed " + str(x) + " " + str(barber_id)))]
    kbs = [[element] for element in kbs]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kbs)
    return keyboard

def date_format(day, month):
    d = datetime.date(datetime.datetime.now().year, month, day)
    return d.strftime("%A %d %b %y")


def date_format_url(date_str):
    l1 = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    l2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    d = dict(zip(l1, l2))

    day = "{:02d}".format(int(date_str.split("_")[0]))
    month = "{:02d}".format(int(d[(date_str.split("_")[1])]))
    year = str(date_str.split("_")[2])
    year = str('20'+year)
    return str(year+"-"+month+"-"+day)


async def dates_list(pick, barber_id):
    start_time = time.time()
    ### Takes service button pick, url_for_barber_id and returns dates list
    waitfor = 700
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    url_barber_chosen = "https://n155779.yclients.com/company:106935?o=" + barber_id
    await page.goto(url_barber_chosen)
    await page.waitForSelector(
        'body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper > div > div > div > div > div > div > div:nth-child(2) > div > div > div')
    service = await page.querySelector(
        'body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper > div > div > div > div > div > div > div:nth-child(2) > div > div > div')
    await service.click()

    await page.waitForSelector('[ng-bind-html^="$"]')
    #await page.waitFor(waitfor)
    services = await page.querySelectorAll('[ng-bind-html^="$"]')
    await services[pick].click()
    await page.waitFor(waitfor)
    url_for_barber_id = await page.evaluate("() => window.location.href")
    print(url_for_barber_id)

    await page.waitForSelector('body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper > div > div > div > div > div > div > div:nth-child(3) > div > div > div > div')
    #await page.waitFor(waitfor)
    dates = await page.querySelector('body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper > div > div > div > div > div > div > div:nth-child(3) > div > div > div > div')
    await dates.click()

    await page.waitForSelector('[data-locator^="working_day"]')
    month = await page.querySelector('[data-locator^="selected_month"]')
    month = await month.getProperty("textContent")
    dates = await page.querySelectorAll('[data-locator^="working_day"]')

    dates_list = []
    l1 = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
          'Декабрь']
    l2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    d = dict(zip(l1, l2))

    for topic in dates:
        title = await topic.getProperty("innerHTML")
        c = date_format(int(await title.jsonValue()), d[await month.jsonValue()])
        dates_list.append(c)

    await browser.close()
    print("dates list time for execution ", (time.time() - start_time))
    return dates_list, url_for_barber_id


def get_buttons_dates(arr, barber_id, service_id):
    kbs = []
    for x in range(len(arr)):
        pick = (arr[x].split()[1]+"_"+arr[x].split()[2]+"_"+arr[x].split()[3])
        kbs = kbs + [InlineKeyboardButton(text=arr[x], callback_data=str("date_button_pushed " + str(pick) + " " + str(barber_id) + "/" + str(service_id)))]
    kbs = [[element] for element in kbs]
    kbs = kbs[:7]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kbs)
    return keyboard


async def times_list(pick, barber_service_pair):
    start = time.time()
    ### Takes dates button pick and callback data (barber and service) and returns times list to choose
    waitfor = 2000
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    url_for_times = "https://n155779.yclients.com/company:106935/idx:0/time?o=" + barber_service_pair.split("/")[0] + \
                          barber_service_pair.split("/")[1]
    url_for_times = url_for_times[:-1]+date_format_url(pick)
    print(url_for_times)
    await page.goto(url_for_times)
  #  await page.waitFor(waitfor)
    await page.waitForSelector('[ng-if^="!$ctrl.isUSAFormat"]')
    url_for_times = await page.evaluate("() => window.location.href")
    times = await page.querySelectorAll('[ng-if^="!$ctrl.isUSAFormat"]')

    times_list = []

    for time_ in times:
        time_ = await time_.getProperty('textContent')
        time_ = await time_.jsonValue()
        times_list.append(time_)

    await browser.close()
    print("times list time for execution ", (time.time() - start))
    return times_list, url_for_times

def get_buttons_times(arr, url_time_choose):

    kbs = []
    kbs2 = []
    for x in range(len(arr[:-5])):
        kbs = kbs + [InlineKeyboardButton(text=arr[x], callback_data=str("time_button_pushed "+str(x) + " " + str(url_time_choose)))]

    kbs = [element for element in kbs]
    for i in range(len(kbs)):
        if i % 4 != 0:
            pass
        else:
            kbs2 = kbs2 + [kbs[i:i + 4]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kbs2)
    return keyboard

async def apr(pick, url):
    ### Takes time button pick and time selection URL and returns approval screen
    waitfor = 2000
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    url_time = "https://n155779.yclients.com/company:106935/idx:0/"+url
    await page.goto(url_time)
    await page.waitForSelector('[ng-if^="!$ctrl.isUSAFormat"]')
    times = await page.querySelectorAll('[ng-if^="!$ctrl.isUSAFormat"]')
    await times[pick].click()
    await page.waitFor(waitfor)
    url_for_approval = await page.evaluate("() => window.location.href")
    dic_ = {"x": 120, "y": 110, "width": 350, "height": 250}
    screenshot = await page.screenshot({"path": "оформить_визит.png", "clip": dic_})
    await browser.close()

    return screenshot, url_for_approval


def get_buttons_approve(url):
    arr = ["Да, всё норм", "Нет, поменять"]
    kbs = []
    for x in range(len(arr)):
        kbs = kbs + [InlineKeyboardButton(text=arr[x], callback_data=str("approve_button_pushed " + str(x) + " " + str(url)))]
    kbs = [[element] for element in kbs]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kbs)
    return keyboard

async def approve_button_pushed(url):
    waitfor = 3000
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    url_apr = "https://n155779.yclients.com/company:106935?"+url
    await page.goto(url_apr)
    await page.waitForSelector(
        "body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper > div > div > div > div > button.y-button.y-button_block.warn-background-color.y-button_filled.y-list-item__order-button.ng-binding.ng-scope")
    button = await page.querySelector(
        "body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper > div > div > div > div > button.y-button.y-button_block.warn-background-color.y-button_filled.y-list-item__order-button.ng-binding.ng-scope")

    await button.click()  ### нажата кнопка "оформить визит"
    await page.waitFor(waitfor)
    final_url = await page.evaluate("() => window.location.href")
    screenshot = await page.screenshot({"path": "final_approval.png"})

    await browser.close()

    return screenshot, final_url


async def zapisatsa(telephone_number, username, url):
    browser = await launch(
        options={
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False
        })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    await page.goto(url)
    await page.waitForSelector('[placeholder="Телефон"]')
    await page.waitFor(2000)
    # telephone
    telephone_entry = await page.querySelector('[placeholder="Телефон"]')
    await telephone_entry.type(telephone_number)

    # name
    name_input = await page.querySelector('#name')
    input_name = username
    await name_input.type(input_name)

    # textarea
    text_area = await page.querySelector('#textarea')
    input_text = "This was send by the bot"
    await text_area.type(input_text)

    # checkbox
    check_box = await page.querySelector('body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper.y-dark-layout > div > div > div > yclients-record-order > div > y-tabs > ng-transclude > y-tab.ng-scope.ng-isolate-scope.js-is-visible > div > ng-transclude > div > form > div:nth-child(3) > y-checkbox > div.md-container > div')
    await check_box.click()


    final_button = await page.querySelector(
        'body > yclients > div > div.ng-scope > div > div > div.h100.y-content-wrapper.y-main-wrapper.y-dark-layout > div > div > div > yclients-record-order > div > y-tabs > ng-transclude > y-tab.ng-scope.ng-isolate-scope.js-is-visible > div > ng-transclude > div > form > button > span')
    await final_button.click()
    await page.waitFor(2000)

    screenshot = await page.screenshot({"path": "final_approval.png"})
    await browser.close()

    return screenshot

#############BEGIN STRUGGLE#########
    # que = Queue()
    # t = Thread(target=lambda q, arg1: q.put(functions.run_async_barbers_list(arg1)), args=(que, functions.barbers_list()))
    # t.start()
    # t.join()
    # barbers_list = que.get()
###############END STRUGGLE###########






