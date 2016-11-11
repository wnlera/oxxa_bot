import vk_api

def auth():
    global vk
    #login, password = '89221811840', 'windazsefvd123333' витя
    login, password = '89505553988', 'Windazsefvd12333%' #окса id: 353056438
    vk_session = vk_api.VkApi(login, password, app_id=5271020, client_secret='tkj3YIhMcxCBdjDcJN5v', token='62642703eb4327bf31455bfc18c7c540df23af723fab0728aaab259e18e376793b0f9b21613cb104989b8')
    try:
        vk_session.vk_login()

    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
    vk = vk_session.get_api()

def sendMsg(idd, msg, forward=None, attach=None):
    global vk
    try:
        vk.messages.setActivity(user_id=353056438, type='typing', peer_id=int(idd)); # Типа печатаем
        vk.messages.send(peer_id=int(idd),message=msg, forward_messages=forward, attachment=attach)
    except:
        print("[MSG] %s не может принять сообщение"%(idd))
        try:
            vk.messages.setActivity(user_id=353056438, type='typing', peer_id=int(idd)); # Типа печатаем
            rndSleep();
            vk.messages.send(user_id=int(idd),message=msg, attachment=attach)
        except:
            print("[MSG] %s не смог принять сообщение!!!!"%(idd))
        else:
            rndSleep()
    else:
        rndSleep()

