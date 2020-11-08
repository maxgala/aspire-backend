import os
rootdir = os.getcwd()
import sys
from datetime import date    
# print(sys.path)
# print(rootdir)
today = date.today().isoformat()
print(today) # '2018-12-05'
truck = dict(
    color = 'blue',
    brand = 'ford',
)


