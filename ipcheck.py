from subprocess import check_output

ips = str(check_output(['ifconfig']))
import re
text = ips
m = re.findall(r'[w]\w+', text)
print(m)
print(re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",str(check_output(['ifconfig', m[0]])))[0])
