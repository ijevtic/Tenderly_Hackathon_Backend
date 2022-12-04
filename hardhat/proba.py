import subprocess
import time

cmd = ['ls']
output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
print(output)