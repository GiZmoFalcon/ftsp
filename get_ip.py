try:
    import re
    import netifaces
    wireless = re.findall(r'[w]\w+', str(netifaces.interfaces()))
    abc = netifaces.ifaddresses(wireless[0])
    ip_addr = abc[netifaces.AF_INET][0]['addr']
    netmask = abc[netifaces.AF_INET][0]['netmask']
    bcast_ip = abc[netifaces.AF_INET][0]['broadcast']
    print(ip_addr + "\n" + bcast_ip + "\n" + netmask)
except Exception:
    text = str(check_output(['ifconfig']))
    m = re.findall(r'[w]\w+', text)
    ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", str(check_output(['ifconfig', m[0]])))
