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

# 'play out all remaining fixtures' - (number of fixtures)^3 (Home Win, Away Win, Draw)
