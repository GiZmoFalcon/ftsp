import socket
from config import *
from random import randint
from threading import Thread
import time
import re
from subprocess import check_output


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
        self.rand_dict = {}
        self.my_rank = randint(1,100)
        print('Host: {0}\nBcast IP: {1}\nRank: {2}'.format(self.host, self.bcast_ip, self.my_rank))

    def broadcast(self, message):
        self.bcast_soc.sendto(message.encode(), (self.bcast_ip, BCAST_PORT))

    def receive_bcast(self):
        print("Starting receiving broadcast")
        while True:
            print("Receiving data")
            msg, addr = self.bcast_soc.recvfrom(1024)
            msg = msg.decode()
            if 'r' in msg:
                if addr[0] != self.host and addr[0] + ':' +str(addr[1]) not in self.rand_dict:
                    self.rand_dict[addr[0] + ':' +str(addr[1])] = int(msg[1:])
                    print("Address: {} Rank: {}".format(addr[0], msg))

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
    print("abc")