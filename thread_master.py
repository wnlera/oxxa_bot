import threading

from thread_messages import ThreadMessages
from thread_sheduler import ThreadSheduler
from vk import auth


class ThreadMaster():
    def auth(self):
        self._vk_ = auth()
        pass

    def __init__(self):
        self._vk_ = auth()
        self._m_worker_ = ThreadMessages(vk=self._vk_)
        self._t_worker_ = ThreadSheduler(vk=self._vk_)

    def start_threads(self):
        self._m_worker_.start()
        self._t_worker_.start()
