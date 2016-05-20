# -*- coding: utf-8 -*-
"""
Created on Fri May 20 22:03:11 2016

@author: Milosh
"""

from subprocess import Popen, PIPE


unrap_path = 'unRap.exe'
sqm_path = 'mission.sqm'
print('sqqqqqm'), sqm_path
p = Popen([unrap_path, sqm_path], stdout=PIPE)
p.wait()
o = [x for x in p.stdout.readlines()]
print(o)
# debugging       