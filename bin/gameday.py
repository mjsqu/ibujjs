#!/usr/bin/python
# Gameday results downloader
# 
# Finds all Island Bay teams and then checks for their fixtures
#
# Improvements
#   - Get junior team names/IDs and set those to be displayed for the morning
#   - Display senior fixtures in the afternoons
#
import requests
import json
import urlparse
import os
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from sportstg import urlq,clubteams,gamestoday,dcthtml
parser = argparse.ArgumentParser(description='Options Videprinter date')
parser.add_argument('-d','--date')
args = vars(parser.parse_args())

d_arg = args['date']
if d_arg is not None:
    print 'Running '+d_arg

# Capture team and competition data
datadir = os.path.join('..','data')
clubfile = os.path.join(datadir,'clubteams.json')
compfile = os.path.join(datadir,'compnames.json')

if not(os.path.isfile(compfile)):
    print 'The competition names are not ready'
else:
    with open(compfile,'r') as f:
        compdict = json.load(f)

if not(os.path.isfile(clubfile)):
    print 'Club file not found building new'
    x = clubteams('112029')

    with open(clubfile,'w') as f:
        json.dump(x,f)

else:
    print 'Using existing club file'
    with open(clubfile,'r') as f:
        x = json.load(f)
# End of capturing team and competition data

# Set date strings
d_run = datetime.now()
if d_arg is not None:
    d_run = datetime.strptime(d_arg,'%Y%m%d')

datestr = d_run.strftime('%d/%m/%y')
filestr = d_run.strftime('%d%m%y')

lastweek = d_run - timedelta(days=7)

if d_arg is not None:
    print datestr
    print filestr

# if a json file with today's leagues in it does not exist, then run the search
todayjson = os.path.join(datadir,'ibucomps_' + filestr + '.json')
htmloutd = {'nt':r'C:\inetpub\wwwroot','posix':r'/var/www/html'}
htmlout = os.path.join(htmloutd[os.name],'res.html')

if d_arg is not None:
    print todayjson

if not (os.path.isfile(todayjson)):
    ct = clubteams('112029')

    tl = []
    for clubteam in ct:
        td = {}
        for key,val in clubteam.items():
            if key == 'compID':
                td[key] = val[0]
            if key == 'teamname':
                td[key] = val
        tl.append(td)
else:
    tl = []
    with open(todayjson,'r') as f:
        tl = json.load(f)

# Run the todaysearch across the list
today = gamestoday(datestr,tl)

# Lookup last week games only for the comps identified in today
#lw = gamestoday(lastweek,tl)

# Update the json with active teams
if not (os.path.isfile(todayjson)):
    active = []
    for rx in today:
        dx = {}
        dx['teamname'] = rx[0]
        dx['compID'] = rx[1]
        active.append(dx)

    active = [dict(t) for t in set([tuple(d.items()) for d in active])]


    with open(todayjson,'w') as f:
        json.dump(active,f)

# Split frow into chunks of 3

# Go through the today list and build a HTML table
# Improvements
#   - Add venue
#   - Add time
#   - Sort by time
#   - Remove repeated code by building an object and joining tags
html = dcthtml(today)

with open(htmlout,'w') as f:
    f.write(html)
