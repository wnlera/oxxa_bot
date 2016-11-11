# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
from urllib.request import urlretrieve
import re
import xlrd
from grabber import getWeekNum, getWeather, getShedUrl, getLastModifiedS
from uti import getCacheProp, jDump, setCacheProp, getLastModified
from vk import sendMsg


def downloadShed(url):
    try:
        st_shed = getCacheProp('st_shed')
    except:
        print("[DownloadShed] ошибка в st_shed")
        st_shed = -1
    dest = "data\\shedules\\xls\\%s.xls" % st_shed
    print("[DownloadShed] Скачиваю %s" % url)
    urlretrieve(url, dest)
    print("[DownloadShed] Расписание скачано!")
    print("%s.xls\n" % st_shed)
    parse_file_to_json("%s" % st_shed)


def parse_file_to_json(file):
    print('[ParseFileToJson] Начинаю парсинг...')
    shed = xlrd.open_workbook("data\\shedules\\xls\\%s.xls" % (file), formatting_info=True)
    sheet = shed.sheet_by_index(0)
    jsonShedules = dict()
    for group in ["ИСБО-01-16"]:
        y = -1
        for rownum in range(sheet.nrows):
            y += 1
            x = -1
            row = sheet.row_values(rownum)
            for c_el in row:
                x += 1
                if str(c_el).rstrip() == group:
                    lessonData = sheet.col_values(x, start_rowx=y + 2, end_rowx=y + 6 * 6)
                    auditoryData = sheet.col_values(x + 1, start_rowx=y + 2, end_rowx=y + 6 * 6)

                    parsedData = [
                        ([lesson, auditory
                          ]) if lesson != "" else ["НЕТ ПАРЫ", ""] for lesson, auditory in
                        zip(lessonData, auditoryData)]
                    packedData = [parsedData[i * 6:i * 6 + 6] for i in range(len(parsedData) // 5)]

        completeShed = []  # Полное расписание. isbo:[{[пара, cond:{1,2,3}]}]
        IDays = [x for x in range(30)[1::2]]  # Нечетные
        IIDays = [x for x in range(30)[2::2]]  # Четные
        jsonWeek = []
        for day in packedData:
            jsonDay = {}  # Разобранное расписание ДНЯ
            lessonNum = 0
            for lesson in day:
                lessonNum += 1
                auditories = re.sub(r" ", r"", lesson[1]).split("\n")
                lesson[0] = " " + lesson[0]

                # I
                try:
                    resI = re.search(r"[^I]I н.", lesson[0])
                except:
                    resI = None
                # II
                try:
                    resII = re.search(r"II н.", lesson[0])
                except:
                    resII = None
                    # d-d
                try:
                    resRng = re.search(r"\d+-\d+ н.", lesson[0])
                except:
                    resRng = None

                if resRng is not None:  # Вытаскиваем диапазон недель
                    rngA, rngB = [int(x) for x in lesson[0][resRng.start():resRng.end() - 3].split('-')]
                    cond = [x for x in range(rngA, rngB)]
                    jsonLesson = [{"lesson": lesson[0][resRng.end() + 1:], "auditory": lesson[1], "cond": cond}]
                    # print(jsonDay)

                elif resI is not None and resII is None:  # одна пара по нч
                    jsonLesson = [{"lesson": lesson[0][resI.end() + 1:], "auditory": lesson[1], "cond": IDays}]

                elif resI is None and resII is not None:  # одна пара по ч
                    jsonLesson = [{"lesson": lesson[0][resII.end() + 1:], "auditory": lesson[1], "cond": IIDays}]

                elif resI is not None and resII is not None:  # пара по ч и пара по нч
                    lessonI = lesson[0][resI.end():resII.start()]
                    lessonII = lesson[0][resII.end():]
                    auditoryI, auditoryII = lesson[1].split("\n")
                    jsonLesson = [{"lesson": lessonI, "auditory": auditoryI, "cond": IDays},
                                  {"lesson": lessonII, "auditory": auditoryII, "cond": IIDays}]

                elif (resI == None and resII == None):
                    cond = IDays + IIDays
                    jsonLesson = [{"lesson": lesson[0], "auditory": lesson[1], "cond": cond}]
                jsonDay[lessonNum] = jsonLesson
            jsonWeek.append(jsonDay)
        jsonShedules[group] = jsonWeek
    jDump("data\\shedules\\json\\%s.json" % file, jsonShedules)
    print('[ParseFileToJson] Парсинг завершен.')
    print('====================')


def getDailyShed(day, week, group):
    with open("data\\shedules\\json\\%s.json" % getCacheProp('st_shed'), mode='r', encoding='utf-8') as f:
        json_data = json.load(f)

    dayData = json_data[group][day]
    shedule = []

    weekNum = week
    lessonCount = 0
    for lessonNum in sorted(dayData):
        for option in dayData[lessonNum]:
            if option['lesson'] != 'EMPTY':
                if weekNum in option['cond']:
                    if option['auditory'] != '':
                        auditory = "(%s)" % option['auditory']
                    else:
                        auditory = ''
                    shedule.append("%s %s" % (option['lesson'].strip().split("\n")[0], auditory))
                    break
            if dayData[lessonNum][-1] == option:
                shedule.append("ОКНО")
    lStart = ''
    lEnd = ''
    for lesson in reversed(shedule):  # Очищаем последние пустые пары
        if lesson.strip() in ['ОКНО', 'НЕТ ПАРЫ']:
            shedule.pop()
        else:
            lEnd = len(shedule) - 1
            break
    # Начало пар
    i = 0
    for lesson in shedule:
        if not lesson in ['ОКНО', 'НЕТ ПАРЫ']:
            break
        i += 1
    startT = ['9:00', '10:45', '12:50', '14:35', '16:20', '18:00', '19:45']
    endT = ['10:35', '12:20', '14:25', '16:10', '17:55', '19:35', '21:20']
    ans = ""
    for x in enumerate(shedule):
        ans += ("%s) [%s-%s]\n%s\n" % (x[0] + 1, startT[x[0]], endT[x[0]], x[1]))
    return ans


def compileShed(group):
    days_of_week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
    print("[ShedCompiler] Начал сборку...")
    dt = datetime.now() + timedelta(days=1)
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
=========================''' % (date, dOw, week, getDailyShed(day, week, 'ИСБО-01-16'), weather)
        print("%s" % s)
        print("[ShedCompiler] Сборка завершена!")
        return s
    else:
        print("[ShedCompiler] Сборка НЕ завершена!")
        return ''



def checkNewShed():
    print("====================")
    try:
        st_shed = getCacheProp('st_shed')
    except:
        print('eRRRRRRRRRRRROr')
        st_shed = 0
    s = getShedUrl()
    print("Url: %s" % s)
    try:
        new = getLastModifiedS(s)
        old = getLastModified()
        if new != old:
            print("Найдено новое расписание")
            sendMsg(30903046, "Я нашла новое расписание, загружаю")
            setCacheProp('st_shed', st_shed + 1)
            setCacheProp('lastm', new)
            return True, s
        else:
            print("Новое расписание не найдено")
            return False, False

    except:
        print("Ошибка при проверке нового расписания")
