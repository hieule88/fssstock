import os
import sys
import matplotlib
import matplotlib.pyplot as plt
from io import StringIO
import urllib, base64

plt.plot(range(10, 20))
fig = plt.gcf()

fig.savefig('C:/Users/Admin/Desktop/temp/imgdata.png', format='png')