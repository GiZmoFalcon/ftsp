import socket
from timerTest import Tissot
from time import sleep
from random import randint
import re
from threading import Thread
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


class Server:
    def __init__(self):
        self.timer = Tissot()
        self.beacon_count = 0
        self.name = "Server"
        self.host, self.bcast_ip = get_ips()
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_soc.bind(('', 5000))
        self.conn_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_soc.bind(('', 5000))
        self.clients_list = {}
        Thread(target=self.timer.start).start()

    def broadcast(self, message):
        self.bcast_soc.sendto(message.encode(), (self.bcast_ip, 5000))

    def discover(self):
        print("Discovering...")
        try:
            self.broadcast("PING from server")
            while True:
                msg, addr = self.conn_soc.recvfrom(1024)
                if addr[0] != self.host:
                    self.clients_list[msg.decode()] = addr[0]
                    print("Client {0} with address {1} added to list".format(msg.decode(), addr[0]))
        except KeyboardInterrupt:
            return

    def send_time(self):
        print("Sending time to receivers...")
        self.broadcast(self.timer.check_time() + "\nTimeSync")

    def beacon(self):
        print("Sending beacons\n")
        b = 0
        try:
            while True:
                b += 1
                self.broadcast("beacon")
                sleep(randint(2, 10))
                print("Beacon number {} sent".format(b))
        except KeyboardInterrupt:
            print("Number of beacons sent: {}".format(b))

    def __del__(self):
        self.bcast_soc.close()
        self.conn_soc.close()

if __name__ == '__main__':
    server = Server()
    Thread(target=server.discover).start()
    Thread(target=server.beacon).start()
    print("Client\tAddress")
    [print("{0}\t{1}".format(key, value)) for key, value in server.clients_list.items()]

