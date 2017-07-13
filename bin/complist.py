#!/usr/bin/python
# Non-functional copy of code lines used to build the id:competition_name dict
# Needs tidy up before it can run 
import requests
import json

url = 'http://websites.sportstg.com/aj_complist.cgi?c=1-4205-0-0-0'

r = requests.get(url)

x = json.loads(r.text)

complist = x['data']
new = complist.replace('<option value =\"','')

new1 = new.replace('</option><option value="',';')
new2 = new1.replace('" >&nbsp;',':')
allcomps = new2[35:]
allcomps1 = allcomps.split(';')

allcomps2 = [x.replace('</option>','') for x in allcomps1]

allcomps3 = [x.replace('1-4205-0-','').replace('-0:',':') for x in allcomps2]

d1 = {}
for x in allcomps3:
	el = x.split(':')
	idx = int(el[0])
	val = ':'.join(el[1:])
	d1[idx] = val

outfile = r'/home/pi/football/data/compnames.json'
with open(outfile,'w') as fx1:
	json.dump(d1,fx1)
