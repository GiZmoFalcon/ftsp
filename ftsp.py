import socket
from config import *
from random import randint
from threading import Thread
import time
import re
from subprocess import check_output
from timerTest import Tissot
import sys


def get_ips():
    try:
        import netifaces
        wireless=re.findall(r'[w]\w+', str(netifaces.interfaces()))
        abc = netifaces.ifaddresses(wireless[0])
        ip_addr=abc[netifaces.AF_INET][0]['addr']
        netmask=abc[netifaces.AF_INET][0]['netmask']
        bcast_ip=abc[netifaces.AF_INET][0]['broadcast']
        return ip_addr, bcast_ip
    except Exception:
        text = str(check_output(['ifconfig']))
        m = re.findall(r'[w]\w+', text)
        ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", str(check_output(['ifconfig', m[0]])))
        return ips[0], ips[1]


class ftsp_client:
    def __init__(self):
        self.host, self.bcast_ip = get_ips()
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_soc.bind(('', BCAST_PORT))
        h, m, s, ms = map(int, input('Enter reference time in HH MM SS MS: '))
        self.timer = Tissot(h, m, s, ms)
        self.timer.start()
        self.rand_dict = {}
        self.my_rank = randint(1,100)
        self.server_flag = None
        self.sync_count = 0
        print('Host: {0}\nBcast IP: {1}\nRank: {2}'.format(self.host, self.bcast_ip, self.my_rank))

    def broadcast(self, message):
        self.bcast_soc.sendto(message.encode(), (self.bcast_ip, BCAST_PORT))

    def receive_bcast(self):
        print("Starting receiving broadcast")
        while True:
            print("Receiving data")
            msg, addr = self.bcast_soc.recvfrom(1024)
            msg = msg.decode()
            if addr[0] != self.host:
                if msg[0] == 'r':
                    if addr[0] + ':' +str(addr[1]) not in self.rand_dict:
                        self.rand_dict[addr[0] + ':' +str(addr[1])] = int(msg[1:])
                        print("Address: {} Rank: {}".format(addr[0], msg))
                        self.is_server()
                elif 'server' in msg:
                    if int(msg.split(' ')[1]) > self.my_rank:
                        self.server_flag = False
                    else:
                        if not self.server_flag:
                            self.server_flag = True
                            self.broadcast('server {}'.format(self.my_rank))
                elif not self.server_flag:
                    msg = list(map(int, msg.split(":")))
                    if self.sync_count == 0:
                        self.timer.set_time(msg[0], msg[1], msg[2], msg[3])
                    else:
                        time = [msg[idx] - val for idx, val in enumerate(self.timer.store_time())]
                        self.timer.update_time(time[0], time[1], time[2], time[3])
                    print(self.timer.check_time(), end="\r")
                    sys.stdout.write("\033[K")
                    self.sync_count += 1

    def is_server(self):
        if max([val for _, val in self.rand_dict.items()]) < self.my_rank:
            self.server_flag = True
            self.broadcast('server %d' % self.my_rank)

    def send_rank(self):
        print("Starting sending broadcast")
        while len(self.rand_dict) <= 8:
            print("Sending data")
            self.broadcast('r' + str(self.my_rank))
            time.sleep(3)
            #print("Sending rank..., current list is"+str(self.rand_dict))

    def __del__(self):
        self.bcast_soc.close()

if __name__ == '__main__':
    client = ftsp_client()
    Thread(target=client.send_rank).start()
    print("In")
    Thread(target=client.receive_bcast).start()
    #rec_thr = thread.start_new_thread(client.receive_bcast, ())
    while True:
        print(client.timer.check_time(),end='\r')
        sys.stdout.write("\033[K")
        if client.server_flag:
            client.broadcast(client.timer.check_time())
            for i in range(5):
                time.sleep(randint(1, 10))
                client.broadcast(client.timer.check_time())
            break