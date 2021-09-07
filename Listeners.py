from typing import Iterator, List, Optional
from yaml import safe_load
import os
import pymqi
import time


def read_conf_qmgrs() -> List[dict]:
    with open('config.yml', 'r') as fin:
        return safe_load(fin)['qmgrs']


class Listeners:

    def __init__(self) -> None:
        self.md = pymqi.MD()
        self.gmo = pymqi.GMO()

        self.gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
        self.gmo.WaitInterval = 1000

        self._configuration = read_conf_qmgrs()
        self._qmgr_container = [self._init_qmgr(opts) for opts in self._configuration]

        self._queue_container = [
            self._init_queue(qmgr, opts) 
            for qmgr, opts in zip(self._qmgr_container, self._configuration)
        ]

        self._iterator = ListenersIterator(self)


    def _conn_info(self, host: str, port: str) -> str:
        return f'{host}({port})'


    def _init_qmgr(self, qmgr_opts: dict) -> pymqi.QueueManager:
        qmgr = pymqi.connect(
            queue_manager=qmgr_opts['queue_manager'], 
            channel=qmgr_opts['channel'], 
            conn_info=f"{qmgr_opts['host']}({qmgr_opts['port']})",
            user=qmgr_opts['user'],
            password=qmgr_opts['password']
        )

        return qmgr

    
    def _init_queue(self, qmgr: pymqi.QueueManager, opts: dict) -> pymqi.Queue:
        return pymqi.Queue(qmgr, opts['queue_name'])


    def upd_iterator(self):
        self._iterator._upd()

    
    def __iter__(self):
        return self._iterator


    def __del__(self):
        for queue in self._queue_container:
            queue.close()
        for qmgr in self._qmgr_container:
            qmgr.disconnect()
        
        self.__del__()


class ListenersIterator:

    def __init__(self, listeners: Listeners) -> None:
        self._index = 0
        self._listeners = listeners


    def _upd(self) -> None:
        self._index = 0
        time.sleep(1)


    def __next__(self) -> Optional[str]:
        if self._index < len(self._listeners._queue_container):
            try:
                index = self._index
                self._index += 1

                message: bytes = self._listeners._queue_container[index].get(
                    None, 
                    self._listeners.md, 
                    self._listeners.gmo
                )
                
                self._listeners.md.MsgId = pymqi.CMQC.MQMI_NONE
                self._listeners.md.CorrelId = pymqi.CMQC.MQCI_NONE
                self._listeners.md.GroupId = pymqi.CMQC.MQGI_NONE

                return message.decode('ascii')

            except pymqi.MQMIError as e:
                if e.comp == pymqi.CMQC.MQCC_FAILED and e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    return

        raise StopIteration


if __name__ == '__main__':
    listeners = Listeners()

    while True:
        for message in listeners:
            print(message)

        listeners.upd_iterator()
