import socket
from config import *
from random import randint
from threading import Thread
import time
import re
from subprocess import check_output


def get_ips():
    text = str(check_output(['ifconfig']))
    m = re.findall(r'[w]\w+', text)
    ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", str(check_output(['ifconfig', m[0]])))
    return ips[0], ips[2]


class ftsp_client:
    def __init__(self):
        self.host, self.bcast_ip = get_ips()
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_soc.bind(('', BCAST_PORT))
        self.rand_dict = {}

        #hello
    def broadcast(self, message):
        self.bcast_soc.sendto(message.encode(), (self.bcast_ip, BCAST_PORT))

    def receive_bcast(self):
        print("afsf")
        while True:
            msg, addr = self.bcast_soc.recvfrom(1024)
            msg = msg.decode()
            if 'r' in msg:
                if addr[0] != self.host:
                    self.rand_dict[addr[0] + ':' +str(addr[1])] = int(msg[1:])
                    #print("Address: {} Rank: {}".format(addr[0], msg))

    def send_rank(self):
        print("hdh")
        while not self.rand_dict:
            time.sleep(3)
            my_rank = randint(1, 100)
            print(self.rand_dict)
            self.broadcast('r' + str(my_rank))

    def __del__(self):
        self.bcast_soc.close()

if __name__ == '__main__':
    client = ftsp_client()
    Thread(target=client.send_rank).start()
    print("In")
    Thread(target=client.receive_bcast).start()
    #rec_thr = thread.start_new_thread(client.receive_bcast, ())
    print("abc")