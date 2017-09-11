import smtplib
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import subprocess

#msg = MIMEText("Dear Yihui, you network visualization on the Social Interaction Graph app is ready to view. Thank you for your support for our academic project!")
#msg['Subject'] = "Your visualization is ready!"
#msg['From'] = "epsb@eltanin.cis.cornell.edu"
#msg['To'] = "yf263@cornell.edu"

# alternative one
#print msg.as_string()
#p = Popen(["/usr/bin/mail"], stdin=PIPE)
#p.communicate(msg.as_string())

# alternative two
#Popen(['/usr/bin/mail','-s','Your visualization is ready to view','yf263@cornell.edu','<<<','Hi,your network visualization on the Social Interaction Graph app is ready to view. Thank you for your support.'],stdin=PIPE)
# similar to alternative two, but still doesn't work
#subprocess.call("mail -s 'Ready' yf263@cornell.edu <<< 'Your viz is ready'",shell=True)

import os
os.system("""mail -s "test" yf263@cornell.edu < dummy.txt""")

