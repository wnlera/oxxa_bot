import re

def rndSleep(delay=0.79, alert=True):
    toSleep = delay + random.randint(2, 4);
    time.sleep(toSleep);

def removeGarbage(text):
    clearText = re.sub(u"[^а-яА-Яa-zA-Z0-9: ]", "", text)
    return clearText;
