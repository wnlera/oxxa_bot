import random

import vk_api

from uti import rndSleep


def auth():
    global vk
    # login, password = '89221811840', 'windazsefvd123333' витя
    login, password = '89505553988', 'Windazsefvd12333%'  # окса id: 353056438
    vk_session = vk_api.VkApi(login, password, app_id=5271020, client_secret='tkj3YIhMcxCBdjDcJN5v',
                              token='62642703eb4327bf31455bfc18c7c540df23af723fab0728aaab259e18e376793b0f9b21613cb104989b8')
    try:
        vk_session.vk_login()

    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
    vk = vk_session.get_api()
    return vk


def sendMsg(idd, msg, forward=None, attach=None):
    global vk
    try:
        vk.messages.setActivity(user_id=353056438, type='typing', peer_id=int(idd));  # Типа печатаем
        vk.messages.send(peer_id=int(idd), message=msg, forward_messages=forward, attachment=attach)
    except:
        print("[MSG] %s не может принять сообщение" % (idd))
        try:
            vk.messages.setActivity(user_id=353056438, type='typing', peer_id=int(idd));  # Типа печатаем
            rndSleep();
            vk.messages.send(user_id=int(idd), message=msg, attachment=attach)
        except:
            print("[MSG] %s не смог принять сообщение!!!!" % (idd))
        else:
            rndSleep()
    else:
        rndSleep()


def sendMeme(idd, guarant=False):
    global vk;
    try:
        if random.randint(0, 135) < 3 and not guarant:
            a = 5 / 0;  # не повезло чуваку, идем в экспешн'''
        ownerId = random.choice([65596623, 90839309, 42923159, 73598440, 45745333, 55307799, 66678575, 73319310])
        wall = vk.wall.get(owner_id=-ownerId, offset=random.randint(1, 1700), count=1);
        post = "wall-%d_%d" % (ownerId, wall['items'][0]['id'])
        msg = random.choice(['Ня', 'Держи)', 'Воть'])
        sendMsg(idd, msg, attach=post)
        print('[SendMeme] Отправила мемчик')
    except:
        sendMsg(idd, random.choice(['Для тебя не нашлось мемасика',
                                    'Не кину',
                                    'Я, конечно, нашла прикол, но, боюсь, ты его не поймешь',
                                    'Нит)',
                                    'Даже я не буду скидывать тебе мемы']))
