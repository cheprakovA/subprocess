import pymqi
import os
from yaml import safe_load 


def read_conf() -> dict:
    with open(os.path.join(os.getcwd(), 'config.yml'), 'r') as fin:
        conf = safe_load(fin)['qmgrs'][0]
        return conf


def put(queue: pymqi.Queue, message: str) -> None:
    queue.put(message)


conf = read_conf()


md = pymqi.MD()
gmo = pymqi.GMO()

gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
gmo.WaitInterval = 5000

qmgr = pymqi.connect(
    queue_manager=conf['queue_manager'], 
    channel=conf['channel'], 
    conn_info=f"{conf['host']}({conf['port']})", 
    user=conf['user'], 
    password=conf['password']
)

queue = pymqi.Queue(qmgr, conf['queue_name'])

put(queue, b'HELL O')

queue.close()
qmgr.disconnect()