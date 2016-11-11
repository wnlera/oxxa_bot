import json
import random
import re

import time


def rndSleep(delay=0.79, alert=True):
    toSleep = delay + random.randint(2, 4)
    time.sleep(toSleep)


def removeGarbage(text):
    clearText = re.sub(u"[^а-яА-Яa-zA-Z0-9: ]", "", text)
    return clearText


def jDump(file, j):
    with open(file, mode='w', encoding='utf-8') as f:
        json.dump(j, f, indent=1, sort_keys=True, ensure_ascii=False)


def getCacheProp(prop):
    with open("data\\cache.json", mode='r', encoding='utf-8') as f:
        json_data = json.load(f)
    s = json_data[prop]
    return s


def setCacheProp(prop, val):
    with open("data\\cache.json", mode='r', encoding='utf-8') as f:
        json_data = json.load(f)
    json_data[prop] = val
    jDump('data\\cache.json', json_data)


def getLastModified():
        with open("data\\cache.json", mode='r', encoding='utf-8') as f:
            json_data = json.load(f)
        lastm = json_data['lastm']
        '''
        except:
            print("[get_st_shed] Error in st_shed")
            st_shed = 0;
        '''
        print("old lastm: %s" % lastm)
        return lastm
