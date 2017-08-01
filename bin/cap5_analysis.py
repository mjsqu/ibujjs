import requests
from bs4 import BeautifulSoup

url='http://websites.sportstg.com/rpt_fixture.cgi'
compid = '458386'
params = {'client':'1-4205-0-'+compid+'-0'}
r = requests.get(url,params=params)

# Parse using BS
s = BeautifulSoup(r.text, 'lxml')

# The club team rows are all in div elements with class = club-team row
ct = s.find('table',attrs={'class':'tableClass table'})

headers = ['ROUND', 'DATE', 'TIME', 'VENUE/COURT', 'HOMESCORE', 'HOME TEAM', 'vs', 'AWAY TEAM', 'AWAYSCORE']
results = [{headers[i]: cell.text.replace(u'\xa0','').strip() for i, cell in enumerate(row.find_all('td')[0:len(headers)])} for row in ct.find_all('tr')]
resdict = [x for x in results[2:len(results)]]

# Build a league table using results that have been played
# Build set of teams
teams = []
for r in resdict:
    teams.append(r['HOME TEAM'])

teams = set(teams)

# Initialise team, p, w, d, l, f, a, pts
tableheads = ['P','W','D','L','F','A','Pts']
tdx = {}
for t in teams:
    td = {}
    for th in tableheads:
        td[th] = 0
    tdx[t] = td

fxt = []
for r in resdict:
    if r['HOMESCORE'] <> '':
        hsc = int(r['HOMESCORE'])
        asc = int(r['AWAYSCORE'])
        tdx[r['HOME TEAM']]['F'] += hsc
        tdx[r['HOME TEAM']]['A'] += asc
        tdx[r['AWAY TEAM']]['F'] += asc
        tdx[r['AWAY TEAM']]['A'] += hsc
        tdx[r['HOME TEAM']]['P'] += 1
        tdx[r['AWAY TEAM']]['P'] += 1
        if hsc > asc:
            tdx[r['HOME TEAM']]['W'] += 1
            tdx[r['AWAY TEAM']]['L'] += 1
            tdx[r['HOME TEAM']]['Pts'] += 3
        elif hsc < asc:
            tdx[r['HOME TEAM']]['L'] += 1
            tdx[r['AWAY TEAM']]['W'] += 1
            tdx[r['AWAY TEAM']]['Pts'] += 3
        else:
            tdx[r['HOME TEAM']]['D'] += 1
            tdx[r['AWAY TEAM']]['D'] += 1
            tdx[r['HOME TEAM']]['Pts'] += 1
            tdx[r['AWAY TEAM']]['Pts'] += 1
    else:
        fxt.append(r)

# Simplify the data - give teams and fixtures integer identifiers
tl = list(teams)

flx = []
for f in fxt:
    d = {}
    d[0] = tl.index(f['HOME TEAM'])
    d[1] = tl.index(f['AWAY TEAM'])
    flx.append(d)

tbx = {}
for k,v in tdx.items():
    tbx[tl.index(k)] = v['Pts']

# flx now contains fixtures list of {0:,1:} dicts, 0 = home, 1 = away
# tbx contains current table {team_index: points}
# Generate the list of dicts that represent possible final tables
maxmin = {k:set(range(1+len([kx for kx,vx in tbx.items() if v < vx]),11-len([kx for kx,vx in tbx.items() if v > vx]))) for k,v in tbx.items()}

i = 0

from itertools import product
for outcome in product(range(3),repeat=len(flx)):
    nt = dict(tbx)
    for n,f in enumerate(outcome):
        # flx[n] is assigned outcome f, which maps to a points increase for...
        if f == 2:
            nt[flx[n][0]] += 1
            nt[flx[n][1]] += 1
        else:
            nt[flx[n][f]] += 3
    # This produces a dict of team:(maxrank,minrank) after set of outcomes
    for k,v in nt.items():
        # Update maxmin by unioning the current positions with the ones from nt
        newpos = set(range(1+len([kx for kx,vx in nt.items() if v < vx]),11-len([kx for kx,vx in nt.items() if v > vx])))
        oldpos = maxmin[k]
        maxmin.update({k:newpos|oldpos})

# 'play out all remaining fixtures' - (number of fixtures)^3 (Home Win, Away Win, Draw)
