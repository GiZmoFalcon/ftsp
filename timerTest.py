import time
import sys
import _thread as thread

COMPL = 0
HOUR = 1
MINUTE = 2
SECOND = 3
MILLISECOND = 4


class Tissot:
    def __init__(self, h=0, m=0, s=0, ms=0):
        # do validation of time sent here!
        self.MilliSeconds = ms
        self.Seconds = s
        self.Minutes = m
        self.Hours = h

    def set_time(self, h=0, m=0, s=0, ms=0):
        # do validation of time sent here!
        self.MilliSeconds = ms
        self.Seconds = s
        self.Minutes = m
        self.Hours = h

    def start(self):
        while True:
            # sys.stdout.write("\033[K")
            time.sleep(0.001)
            if (self.MilliSeconds < 1000):
                self.MilliSeconds += 1

            else:
                self.MilliSeconds = 0
                if (self.Seconds < 60):
                    self.Seconds += 1

                else:
                    self.Seconds = 0
                    if (self.Minutes < 60):
                        self.Minutes += 1

                    else:
                        self.Minutes = 0
                        if (self.Hours < 24):
                            self.Hours += 1

                        else:
                            self.Hours = 0
            # print("Time:"+str(self.Hours)+":"+str(self.Minutes)+":"+str(self.Seconds)+":"+str(self.MilliSeconds), end="\r")
            pass

    def update_time(self, h=0, m=0, s=0, ms=0):
        self.MilliSeconds += ms
        if (self.MilliSeconds >= 1000):
            self.MilliSeconds -= 1000
            self.Seconds += 1
        self.Seconds += s
        if (self.Seconds >= 60):
            self.Seconds -= 60
            self.Minutes += 1
        if (self.MilliSeconds < 0):
            self.MilliSeconds += 1000
            self.Seconds -= 1
        if (self.Seconds < 0):
            self.Seconds += 60
            self.Minutes -= 1
        self.Minutes += m
        self.Hours += h

    def check_time(self, choice=COMPL):
        return {
            COMPL: (str(self.Hours) + ":" + str(self.Minutes) + ":" + str(self.Seconds) + ":" + str(self.MilliSeconds)),
            HOUR: str(self.Hours),
            MINUTE: str(self.Minutes),
            SECOND: str(self.Seconds),
            MILLISECOND: str(self.MilliSeconds)
        }[choice]

    def store_time(self):
        return self.Hours, self.Minutes, self.Seconds, self.MilliSeconds


# def store_time(self):
#		return self.Hours,self.Minutes,self.Seconds,self.MilliSeconds

def main():
    timerC = Tissot(23, 59, 59, 999)
    thread.start_new_thread(timerC.start, ())
    print("Out!")
    while True:
        print(timerC.check_time(), end="\r")
        print("\n\nIN")
        sys.stdout.write("\033[K")
        print("\n\nIN")
        pass


if __name__ == '__main__':
    main()
