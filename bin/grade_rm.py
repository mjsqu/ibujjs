#!/usr/bin/python
# At 2pm remove the non-Grade comps
import json
from datetime import datetime

d_run = datetime.now()

filestr = d_run.strftime('%d%m%y')

compfile = '/home/pi/football/data/ibucomps_'+filestr+'.json'

with open(compfile,'r') as f:
    x = json.load(f)

print 'Length before removal:'+str(len(x))

with open('/home/pi/football/data/compnames.json','r') as f:
    c = json.load(f)

newx = []
for k in x:
    try:
        compname = c[k['compID']]
        if 'Grade' not in compname:
            newx.append(k)
    except:
        pass

print 'Length after removal:'+str(len(newx))

with open(compfile,'w') as f:
    json.dump(newx,f)
