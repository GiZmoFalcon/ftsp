from timerTest import Tissot
import socket
from threading import Thread
from collections import defaultdict
from datetime import datetime, timedelta
import sys
import re
from subprocess import check_output


def time_difference(time_1, time_2):    # To subtract 2 timestamps and convert them to milliseconds
    time_1, time_2 = ':'.join(list(map(str, time_1))), ':'.join(list(map(str, time_2)))
    print("Own time " + time_1 + " Receiver's time" + time_2)
    FMT = '%H:%M:%S:%f'
    time_1 = datetime.strptime(time_1, FMT)
    time_2 = datetime.strptime(time_2, FMT)
    time = time_2 - time_1
    i = -1
    if time_1 > time_2:
        return int((time_1 - time_2).total_seconds() * 1000)
    return int((time_2 - time_1).total_seconds() * -1000)


def millisec2stamp(ms):     # To convert milliseconds to [hh, mm, ss, ms]
    return datetime.fromtimestamp(ms/1000).strftime("%H:%M:%S:%f")


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


class Mote:
    def __init__(self, name):
        self.name = name
        self.host, self.bcast_ip = get_ips()
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_soc.bind(('', 5000))
        self.conn_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_soc.bind(('', 5000))
        self.server_address = ""
        self.timer = None
        self.pr_bcast_time = None
        self.beacon_count = 0
        self.offset = defaultdict(int)
        self.timer_started = False

    def broadcast(self, message):
        self.bcast_soc.sendto(message.encode(), (self.bcast_ip, 5000))

    def bcast_receive(self):
        FMT = '%H:%M:%S:%f'
        try:
            while True:
                msg, addr = self.bcast_soc.recvfrom(1024)
                msg = msg.decode()

                if "server" in msg:     # Discovery Reply
                    self.conn_soc.sendto(self.name.encode(), (addr[0], 5000))
                    self.server_address = addr[0]
                    print("Sending name to server with address {}".format(addr[0]))

                elif "TimeSync" in msg:      # Timestamp sent by server
                    msg = list(map(int, msg.split(' ')[0].split(":")))
                    self.timer = Tissot(msg[0], msg[1], msg[2], msg[3])
                    Thread(target=self.timer.start).start()
                    self.timer_started = True
                    print("Timer started".format(self.beacon_count), end="\r")

                elif "beacon" in msg:       # Beacon sent by server
                    self.beacon_count += 1
                    self.pr_bcast_time = self.timer.store_time()
                    self.broadcast(":".join(list(map(str, self.pr_bcast_time))))    # Broadcasting beacon received time
                    print("Beacon no. {} received".format(self.beacon_count))

                elif addr[0] != self.host:  # Broadcast received from another mote
                    time2 = list(map(int, msg.split(":")))
                    time_diff = time_difference(self.pr_bcast_time, time2)
                    self.offset[addr[0]] = int(((self.beacon_count - 1) * self.offset[addr[0]] + time_diff) / \
                                            self.beacon_count)  # Offset calculation formula
                    present_time = datetime.strptime(self.timer.check_time(), FMT)
                    if self.offset[addr[0]] < 0:
                        present_time = present_time - timedelta(milliseconds=self.offset[addr[0]]/2)
                    else:
                        present_time = present_time + timedelta(milliseconds=self.offset[addr[0]]/2)
                    present_time = list(map(int, str(present_time.strftime('%H %M %S %f')).split(" ")))
                    present_time[3] = int(present_time[3]/1000)
                    # Updating timer
                    self.timer.set_time(present_time[0], present_time[1], present_time[2], present_time[3])
                    print("Timer updated from address {}".format(addr[0]))

        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    mote = Mote(input("Enter client's name:"))
    mote.bcast_receive()
