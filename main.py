# -*- coding: utf-8 -*-

#MIREA breezy bot

import xlrd
import re
from datetime import datetime, timedelta
import time
import requests
import os
import random
import json
import string
import signal

import threading
from urllib.request import urlretrieve, urlopen
from bs4 import BeautifulSoup
from telebot import util

from grab import Grab

def getLastModified(type, url=''):
    if type == 'remote':
        r = requests.head(url)
        lastm = r.headers['Last-Modified']
        print("new lastm: %s"%lastm)
        return lastm
    elif type == 'local':
        with open("data\\cache.json", mode='r', encoding='utf-8') as f:
            json_data = json.load(f);
        lastm = json_data['lastm']
        '''
        except:
            print("[get_st_shed] Error in st_shed")
            st_shed = 0;
        '''
        print("old lastm: %s"%lastm)
        return lastm;        

def jDump(file, j):
    with open(file, mode='w', encoding='utf-8') as f:
        json.dump(j, f, indent=1, sort_keys=True, ensure_ascii=False)  

def getCacheProp(prop):
    with open("data\\cache.json", mode='r', encoding='utf-8') as f:
        json_data = json.load(f);
    s = json_data[prop]
    return s;

def setCacheProp(prop, val):
    with open("data\\cache.json", mode='r', encoding='utf-8') as f:
        json_data = json.load(f);
    json_data[prop] = val;
    jDump('data\\cache.json', json_data)


def downloadShed(url):
    try:
        st_shed = getCacheProp('st_shed')
    except:
        print("[DownloadShed] ошибка в st_shed")
        st_shed = -1;
    dest = "data\\shedules\\xls\\%s.xls"%st_shed
    print("[DownloadShed] Скачиваю %s"%url)
    urlretrieve(url, dest)
    print("[DownloadShed] Расписание скачано!")
    print("%s.xls\n"%st_shed)
    parseFileToJson("%s"%st_shed)  

def getWeekNum():
    url = 'https://www.mirea.ru/'
    g = Grab()
    try:
        g.go(url)
    except:
        rndSleep()
        g.go(url)
    g = g.doc.select('//div[@class="first_page_week col2_right_conteiner_item"]').text()
    r = re.compile("\d+-")
    return int(re.search(r, g).group(0)[0:-1]);

def sendMeme(idd, guarant=False):
    global vk;
    try:
        if random.randint(0,135) < 3 and not guarant:
            a = 5 / 0; # не повезло чуваку, идем в экспешн'''
        ownerId = random.choice([65596623,90839309,42923159,73598440,45745333,55307799,66678575,73319310])
        wall = vk.wall.get(owner_id=-ownerId, offset=random.randint(1,1700), count=1);
        post = "wall-%d_%d" % (ownerId, wall['items'][0]['id'])
        msg = random.choice(['Ня','Держи)','Воть'])
        sendMsg(idd, msg, attach=post)
        print('[SendMeme] Отправила мемчик')
    except:
        sendMsg(idd,random.choice(['Для тебя не нашлось мемасика',
                                   'Не кину',
                                   'Я, конечно, нашла прикол, но, боюсь, ты его не поймешь',
                                   'Нит)',
                                   'Даже я не буду скидывать тебе мемы']))

def parseFileToJson(file):
    print('[ParseFileToJson] Начинаю парсинг...')
    shed = xlrd.open_workbook("data\\shedules\\xls\\%s.xls"%(file),formatting_info=True);
    sheet = shed.sheet_by_index(0)
    jsonShedules = dict();
    for group in ["ИСБО-01-16"]:
        y = -1
        for rownum in range(sheet.nrows):
            y += 1;
            x = -1;
            row = sheet.row_values(rownum)
            for c_el in row:
                x += 1;
                if str(c_el).rstrip() == group:
                    lessonData = sheet.col_values(x, start_rowx=y+2, end_rowx=y+6*6)
                    auditoryData = sheet.col_values(x+1, start_rowx=y+2, end_rowx=y+6*6)
                    
                    parsedData = [
                        ([lesson, auditory
                         ]) if lesson!="" else ["НЕТ ПАРЫ", ""] for lesson, auditory in zip(lessonData, auditoryData)]
                    packedData = [parsedData[i*6:i*6+6] for i in range(len(parsedData)//5)]
        
        completeShed = [] # Полное расписание. isbo:[{[пара, cond:{1,2,3}]}]
        IDays = [x for x in range(30)[1::2]] # Нечетные
        IIDays = [x for x in range(30)[2::2]] # Четные
        jsonWeek = [];
        for day in packedData:
            jsonDay = {}; # Разобранное расписание ДНЯ
            lessonNum = 0;
            for lesson in day:
                lessonNum += 1;
                auditories = re.sub(r" ", r"", lesson[1]).split("\n")
                lesson[0] = " " + lesson[0]
                
                # I
                try:
                    resI = re.search(r"[^I]I н.", lesson[0])
                except:
                    resI = None;
                # II
                try:
                    resII = re.search(r"II н.", lesson[0])
                except:
                    resII = None;   
                # d-d
                try:
                    resRng = re.search(r"\d+\-\d+ н.", lesson[0])
                except:
                    resRng = None;            
                
                if resRng != None: # Вытаскиваем диапазон недель
                    rngA, rngB = [int(x) for x in lesson[0][resRng.start():resRng.end()-3].split('-')]
                    cond = [x for x in range(rngA, rngB)]
                    jsonLesson = [{"lesson":lesson[0][resRng.end()+1:], "auditory":lesson[1], "cond":cond}]
                    #print(jsonDay)
                    
                elif (resI != None and resII == None): # одна пара по нч
                    jsonLesson = [{"lesson":lesson[0][resI.end()+1:], "auditory":lesson[1], "cond":IDays}]
                    
                elif (resI == None and resII != None): # одна пара по ч
                    jsonLesson = [{"lesson":lesson[0][resII.end()+1:], "auditory":lesson[1], "cond":IIDays}]
                    
                elif (resI != None and resII != None): # пара по ч и пара по нч
                    lessonI = lesson[0][resI.end():resII.start()]
                    lessonII = lesson[0][resII.end():]
                    auditoryI, auditoryII = lesson[1].split("\n")
                    jsonLesson = [{"lesson":lessonI, "auditory":auditoryI, "cond":IDays},{"lesson":lessonII, "auditory":auditoryII, "cond":IIDays}]
                
                elif (resI == None and resII == None):
                    cond = IDays + IIDays
                    jsonLesson = [{"lesson":lesson[0], "auditory":lesson[1], "cond":cond}]
                jsonDay[lessonNum] = jsonLesson
            jsonWeek.append(jsonDay)
        jsonShedules[group] = jsonWeek;
    jDump("data\\shedules\\json\\%s.json"%file, jsonShedules)
    print('[ParseFileToJson] Парсинг завершен.')
    print('====================')
    
def getDailyShed(day, week, group):
    with open("data\\shedules\\json\\%s.json"%getCacheProp('st_shed'), mode='r', encoding='utf-8') as f:
        json_data = json.load(f);
    
    dayData = json_data[group][day]
    shedule = [];
    
    weekNum = week;
    lessonCount = 0;
    for lessonNum in sorted(dayData):
        for option in dayData[lessonNum]:
            if option['lesson'] != 'EMPTY':
                if weekNum in option['cond']:
                    if option['auditory'] != '':
                        auditory = "(%s)"%option['auditory']
                    else:
                        auditory = ''
                    shedule.append("%s %s"%(option['lesson'].strip().split("\n")[0], auditory))
                    break
            if dayData[lessonNum][-1] == option:
                shedule.append("ОКНО")
    lStart = ''
    lEnd = ''
    for lesson in reversed(shedule): # Очищаем последние пустые пары
        if lesson.strip() in ['ОКНО','НЕТ ПАРЫ']:
            shedule.pop();
        else:
            lEnd = len(shedule)-1
            break
    # Начало пар
    i = 0
    for lesson in shedule:
        if not lesson in ['ОКНО','НЕТ ПАРЫ']:
            lStart = i;
            break
        i += 1
    startT = ['9:00', '10:45', '12:50', '14:35', '16:20', '18:00', '19:45']
    endT = ['10:35', '12:20', '14:25', '16:10', '17:55', '19:35', '21:20']
    ans = ""
    for x in enumerate(shedule):
        ans += ("%s) [%s-%s]\n%s\n"%(x[0]+1, startT[x[0]], endT[x[0]],x[1]))
    return ans

def getWeather():
    global weather_forecast;
    url = "http://api.wunderground.com/api/0c25613f6371174e/forecast/q/Russia/Moscow.json"
    response = requests.get(url)
    parsed_data = response.json()['forecast']['simpleforecast']['forecastday'];
    
    ic = 0;
    for day in parsed_data[1:2]:
        #date = "%s.%s.%s (%s)"%(day['date']['day'],day['date']['month'],day['date']['year'],day['date']['weekday'])
        temperature = day['high']['celsius'] # Температура днем
        cond = day['conditions'] # Условия
        wind = day['avewind']['mph'] # Ветер м/c
        PoP = day['pop'] # Шанс осадков в этот день
        #humidity = day['avehumidity'] # Влажность
        #qpf = max(day['qpf_allday']['mm'], day['snow_allday']['mm']) # Осдаки мм (max из снега и дождя)
        
        summary = '''%s
Температура днем: %s°С
Ветер: %s м/с
Вероятность осадков: %s%%'''%(cond, temperature, wind, PoP)
    return summary




def checkNewShed():
    print("====================")
    try:
        st_shed = getCacheProp('st_shed')
    except:
        print('eRRRRRRRRRRRROr')
        st_shed = 0;
    s = getShedUrl()
    print("Url: %s"%s)
    try:
        new = getLastModified('remote', s)
        old = getLastModified('local')
        if new != old:
            print("Найдено новое расписание")
            sendMsg(30903046, "Я нашла новое расписание, загружаю")
            setCacheProp('st_shed', st_shed+1);
            setCacheProp('lastm', new)
            return (True,  s)            
        else:
            print("Новое расписание не найдено")
            return (False, False)            
            
    except:
        print("Ошибка при проверке нового расписания")

days_of_week = ['ПН','ВТ','СР','ЧТ','ПТ','СБ']
def compileShed(group):
    print("[ShedCompiler] Начал сборку...")
    dt = datetime.now()+timedelta(days=1)
    day = datetime.weekday(dt)
    if day != 5:
        print('[CompileShed] Day != 5')
        week = getWeekNum();
        if day == 6 or day == 0:
            day = 0
            week += 1
        date = datetime.strftime(dt, "%d.%m.%y")
        dOw = days_of_week[day]
        weather = getWeather()
    
        s = '''=========================
Информация на %s (%s)
%s-я неделя.
%s
Погода:
%s
========================='''%(date, dOw, week, getDailyShed(day, week, 'ИСБО-01-16'), weather)
        print("%s"%s)
        print("[ShedCompiler] Сборка завершена!")
    else:
        print("[ShedCompiler] Сборка НЕ завершена!")
    return s
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\





vk = 0;
authIn();
pollServ = vk.messages.getLongPollServer()
m_ts = pollServ['ts']
m_key = pollServ['key']
m_server = pollServ['server']

#Слушатель сообщений=========================================================
def messageListener():
    global m_key, m_server, m_ts, vk
    print('[MessageListener] Started!')
    rndSleep(delay=5)
    while True:
        try:
            getUpdate(m_key=m_key, m_server=m_server);
        except Exception as error_msg:# relogin, reconnect
            print("[MessageListener] " + str(error_msg))
            while True:
                try:
                    authIn()
                    pollServ = vk.messages.getLongPollServer()
                    m_ts = pollServ['ts']
                    m_key = pollServ['key']
                    m_server = pollServ['server']                
                    break
                except Exception as error_msg:
                    print("[MessageListener] Login error" + str(error_msg))

#Слушатель времени и отправки расписания========================================
def timeWorker():
    global vk
    print('[TimeWorker] Started!')
    rndSleep(delay=5)
    while True:
        timeChecked = getCacheProp('time_checked')
        dt = datetime.now()
        if dt.hour > 14 or dt.hour < 2:
            print('[TimeWorker] Пришло время расписания')
            if not timeChecked:
                print('##########################################################')
                newShed = checkNewShed()
                if newShed[0]:
                    downloadShed(newShed[1]);
                print('---338')
                print('[TimeWorker] Начинаю рассылку...')
                shed = compileShed('ИСБО-01-16')
                    
                conf = vk.messages.getChat(chat_id=2)
                ids = conf['users']
                #--------PROTECT
                ids2 = ids
                ids2.append(123846625);
                if len(ids2)-1 == len(ids):
                    print("[TimeWorker] Alla added successfully")
                    ids = ids2
                #--------PROTECT
                print("ids: %s"%ids)
                for idd in ids:
                    sendMsg(idd, shed)
                print('[TimeWorker] Расписание доставлено')
                print('##########################################################')
            timeChecked = True
            setCacheProp('time_checked', timeChecked)
        else:
            print('---352')
            timeChecked = False             
            setCacheProp('time_checked', timeChecked) 
        rndSleep(3600)


#Обработчик сообщений
def getUpdate(m_key=0, m_server=0):
    global m_ts
    r = requests.get("https://%s?act=a_check&key=%s&ts=%s&wait=20&mode=2"%(m_server, m_key, m_ts))
    r = r.json()
    m_ts = r['ts']
    r = r['updates']
    r = [x for x in r if (x[0] == 4)] # Выкидываем все события, кроме сообщений
    r = [x for x in r if (vk.messages.getById(message_ids=x[1])['items'][0]['out'] == 0)]# Выкидываем собств сообщ
    '''
    if r != []:
        print(r)
    '''
    for message in r:
        idd = message[3]
        msg = message[6]
        if len(msg) > 0:
            pass
        #print("<%s> %s"%(idd, msg))
        command = str(removeGarbage(msg)).lower().strip() # В нижний регистр
        #print("---->%s"%command)
        #command = list(scommand.split(' ')); # Переводим в список
         
        if 'окс' in command and 'расп' in command:
            with open("data\\cache.json", mode='r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f);
                    timeChecked = json_data['time_checked']
                except:
                    timeChecked = False;
            if timeChecked:
                msg = random.choice(['Я уже рассыла сегодня расписание',
                                     'Сегодня я уже рассылала расписание',
                                     'Нет, я уже рассылала расписание сегодня'])
            else:
                msg = random.choice(['Я отправляю расписание по вечерам',
                                     'Я сама отправлю расписание вечером',
                                     'Нит))0))'])
            sendMsg(idd, msg)
              
        if 'окс' in command:
            if 'вконф' in command: # окса вконф текст
                sendMsg(2, command[1:]);
            elif 'мем' in command: # окса мем
                if random.randint(0,100) < 21:
                    sendMsg(idd, random.choice(['Ща, сек)', 'Сейчас, выберу годненький и отправлю)', 'Сейчас)']))
                    rndSleep()
                    sendMeme(idd, guarant=True)
                else:
                    sendMeme(idd)
            elif 'скажи' in command: # окса мем
                if random.randint(0,100) > 10:
                    try:
                        if '150' in command and ('сколько' in command or 'чему равно' in command):
                            sendMsg(idd, 'Очень смешно -_-')
                        else:
                            end_id = re.search('скажи', command).span()[1]
                            print(command[end_id:])
                            sendMsg(idd,command[end_id:])
                    except Exception as err:
                        print(err)
                        sendMsg(idd,'Ну и что мне сказать?')
                else:
                    sendMsg(idd, random.choice(['Не скажу', 'Не хочу', 'Не буду']))
            elif any(x in command for x in ['прив','хай','здравств']):
                sendMsg(idd, random.choice(['Приветик)',
                                            'Привет',
                                            'Здравствуй',
                                            'Вечер в хату))']))
        elif 'жопа' in command:
            sendMsg(idd, "Да, жопа!")
        # Ты молодец -> сама я знаю *** Московский технологисч.....
        elif ('красава' in command):
            sendMsg(idd, random.choice(["КРАСАВА","КРАСАААВА","Красава!!!"]))
        elif 'кинь динозаврика' in command:
            msg='''─────────██████ 
───────███▄████ 
───────██████ 
───────█████ 
────────███████ 
█───────█████ 
██────█████████ 
███──███████──█ 
████████████ 
████████████ 
─██████████ 
──█████████ 
────██████ 
────███─██ 
────██───█ 
────█────█ 
────██───██
'''
            sendMsg(idd, msg)
        elif 'секретная пасхалка' in command:
            msg='''
──────────────────────────────────────
─▄▄▄───────────▄▄▄▄▄▄▄────────────────
█▀░▀█──────▄▀▀▀░░░░░░░▀▀▄▄────────────
█░░░░█───▄▀░░░░░░░░░░░░░░░▀▄───────▄▄▄
█▄░░░▀▄▄▀░░██░░░░░░░░░░░░░░▀█────█▀▀░█
─█░░░░█▀░░░▀░░░░░░░░██░░░░░░▀█─▄█░░░░█
─▀█░░▄█░░░░░░░▄▄▄░░░░▀░░░░░░░███░░░░█▀
──█▄░█░░░░░▄███████▄░░░░░░░░░█▀░░░░▄▀─
──▀█░█░░░░▄██████████░░░░░░░▄█░░░░▄▀──
───███░░░░███████████░░░░░░▄█░░░░█▀───
────█░░░░░██████████▀░░░░░░█░░░░█▀────
────█░░░░░░▀███████▀░░░░░░░█▄▄▄▀──────
────█░░░░░░░░▀▀▀▀░░░░░░░░░░░▀█────────
────█░░░░░░░░░░░░░░░░░░░░░░░░█────────
────█░░░░░░░░░░░░░░░░░░░░░░░░█────────
────█░░░░░░░░░░░░░░░░░░░░░░░░█────────
──────────────────────────────────────
───█──█─█──█─█──█─█▀▀▀█─█▀▀█─█──█─────
───█▀▀█─█──█─█▄▄█─█───█─█────█──█─────
───█──█─█▄▄█────█─█▄▄▄█─█▄▄█─█▄▄█─────
──────────────────────────────────────
'''
            sendMsg(idd, msg)

try:
    threading.Thread(target=messageListener).start()
except:
    print("Message Listener crashed")

try:
    threading.Thread(target=timeWorker).start()
except:
    print("Time Worker crashed")

#timeWorker()