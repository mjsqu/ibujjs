# Gameday results downloader
# 
# Finds all Island Bay teams and then checks for their fixtures
#
# Improvements
#   - Get junior team names/IDs and set those to be displayed for the morning
#   - Display senior fixtures in the afternoons
#   - Display drinks prices
#   - Display coffee menu
#
import requests
import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

def urlq(url):
    parsed = urlparse.urlparse(url)
    team_info = parsed.query
    url_d = urlparse.parse_qs(team_info)
    return url_d

def clubteams(tid):
    # Sportstg identifiers are in the form:
    # 1-assoc-club-league-team
    assoc_id = '1-4205-0-0-0'
    # Represents the club - e.g. Island Bay, North Wellington United
    club_id = '1-4205-'+tid+'-0-0'
    # Base URL for the websites
    url = 'http://websites.sportstg.com'

    # Club info cgi script
    cgi = 'club_info.cgi'

    url = url + '/' + cgi

    # Parameters for the cgi
    params = {'c': club_id, 'a': 'TEAMS'}

    # Perform the request, storing response in r
    r = requests.get(url=url, params=params)

    # Parse using BS
    s = BeautifulSoup(r.text, 'lxml')

    # The club team rows are all in div elements with class = club-team row
    ct = s.find_all('div',attrs={'class':'club-team-row'})

    # Initialise the team list
    t = []

    # Loop through the teams at Island Bay
    for teamrow in ct:
        # link identifies a competition that the team is in
        element = teamrow.find('h3').find('a')
        # the text of the <a> element is the team name
        team = element.text
        # the target reference is the link which we will parse
        link = element['href']
        # Use urlq function to parse out the link, the return 'u' contains a dict of parameters
        u = urlq(link)
        # Add teamname to the dictionary, giving us full data on the team
        # Usually:
        # compID - Competition ID
        # client - club_id, already known as the originator of the link
        # id - the team ID
        u['teamname'] = team
        # Ignore previous competitions (inactive)
        if 'previous-comps' not in teamrow.attrs['class']:
            t.append(u)

    return t


# gamestoday function returns a set of competitions that can be iterated over
def gamestoday(datestr,teamlist):
    if datestr == '':
        datestr = datetime.now().strftime('%d/%m/%y')

    # Fixture report column names
    headers = ['ROUND', 'DATE', 'TIME', 'VENUE/COURT', 'HOMESCORE', 'HOME TEAM', 'vs', 'AWAY TEAM', 'AWAYSCORE']

    today_comps = []

    requestcount = 0

    # Loops through all possible fixture report pages for Island Bay teams and stores compIDs in a JSON file
    for tx in teamlist:
        url='http://websites.sportstg.com/rpt_fixture.cgi'
        teamname = tx['teamname']
        compid = tx['compID']
        params = {'client':'1-4205-112029-'+compid+'-0'}
        r = requests.get(url,params=params)

        requestcount+=1

        # Parse using BS
        s = BeautifulSoup(r.text, 'lxml')

        # The club team rows are all in div elements with class = club-team row
        ct = s.find('table',attrs={'class':'tableClass table'})

        results = [{headers[i]: cell.text.replace(u'\xa0','').strip() for i, cell in enumerate(row.find_all('td')[0:len(headers)])} for row in ct.find_all('tr')]
        resdict = [x for x in results[2:len(results)] if x['DATE'][:8] == datestr]
        if len(resdict) > 0:
            today_comps.append([teamname,compid,resdict])

    print requestcount
    return today_comps

def dcthtml(today):
  # dict layout for html
  html = ''
  for i,frow in enumerate(today):
    # Each element of today contains
    # 0 - IBU team name
    # 1 - competitionID
    # 2 - dict of fixtures
    ibuteam = frow[0]
    compid = frow[1]
    df = frow[2]
    html += '<div class="lge" id="h'+str(i)+'">'
    try:
      html += compdict[compid]
    except:
      html += 'Unknown Competition'
    html += '</div>'
    # Competition header complete
    # Table header start
    html += '<table id="rn'+str(i)+'">'
    html += '<tr>'
    #html += '<th class="comp"/>'
    html += '<th class="venue"/>'
    html += '<th class="time"/>'
    html += '<th class="team">HOME</th>'
    html += '<th class="score"></th>'
    html += '<th class="divider"></th>'
    html += '<th class="score"></th>'
    html += '<th class="team">AWAY</th>'
    html += '</tr>'
    # Table header complete
    for dfixs in df: 
        html += '<tr>'
        venue = dfixs['VENUE/COURT']
        fixtime = dfixs['TIME']
        hometeam = dfixs['HOME TEAM']
        awayteam = dfixs['AWAY TEAM']
        homescore = dfixs['HOMESCORE']
        awayscore = dfixs['AWAYSCORE']
        if ibuteam == hometeam:
            hometeam = '<b>'+hometeam+'</b>'
        if ibuteam == awayteam:
            awayteam = '<b>' + awayteam + '</b>'
        #html += '<td class="comp">' + compid + '</td>'
        html += '<td class="venue">' + venue + '</td>'
        html += '<td class="time">' + fixtime + '</td>'
        html += '<td class="team">' + hometeam + '</td>'
        html += '<td class="score">' + homescore + '</td>'
        html += '<td class="divider">' + ' - ' + '</td>'
        html += '<td class="score">' + awayscore + '</td>'
        html += '<td class="team">' + awayteam + '</td>'
        html += '</tr>\n'
    html += '</table>'
  return html

