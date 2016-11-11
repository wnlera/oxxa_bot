from datetime import datetime
import threading

from shedule_master import checkNewShed, downloadShed, compileShed
from uti import rndSleep, getCacheProp, setCacheProp
from vk import sendMsg


class ThreadSheduler(threading.Thread):
    def __init__(self, vk):
        threading.Thread.__init__(self)
        self.vk = vk

    def run(self):
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

                    conf = self.vk.messages.getChat(chat_id=2)
                    ids = [30903046]  # conf['users']
                    # --------PROTECT
                    ids2 = ids
                    # ids2.append(123846625);
                    if len(ids2) - 1 == len(ids):
                        print("[TimeWorker] Alla added successfully")
                        ids = ids2
                    # --------PROTECT
                    print("ids: %s" % ids)
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
