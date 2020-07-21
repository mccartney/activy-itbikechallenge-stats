import json
from botocore.vendored import requests
import datetime

def authenticate():
   URL='https://players.v3.activy.pl/auth/connect/token' 
   headers = {
         'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0' ,
         'Accept': '*/*', 
         'Accept-Language': 'en-GB,en;q=0.7,en-US;q=0.3' ,
         'Referer': 'https://stats.activy.pl', 
         'Authorization': 'Basic REDACTED==',
         'Content-Type': 'application/x-www-form-urlencoded', 
         'Origin': 'https://stats.activy.pl', 
         'DNT': '1', 
         'TE': 'Trailers'
   }
   data = 'grant_type=password&scope=openid+email+offline_access+activy.players+activy.contests+activy.rides&username=REDACTED&password=REDACTED'
   r = requests.post(URL, headers = headers, data = data)
   access_token = json.loads(r.text)["access_token"]
   if (r.status_code != 200):
       raise Exception("Failed to authenticate {}".format(r.status_code))
   return access_token

def requestUrl(auth, URL, additionalData="", date = None, activityType = -1):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.7,en-US;q=0.3',
        'Referer': 'https://stats.activy.pl/rankings',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth,
        'Origin': 'https://stats.activy.pl', 
        'DNT': '1',
        'Connection': 'keep-alive',
        'TE': 'Trailers',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }    
 
    if not date: 
        date = datetime.datetime.now().isoformat("T")[:-3]+"Z"

    data =  '{%s"ContestId":"8afb74ea-401f-430d-afc3-b527b34a0ac2","Day":"%s","ActivityType":%d,"Type":0}' % (additionalData, date, activityType)
    
    print("Requesting {}\n, {}\n, {}\n".format(URL, headers, data))
    
    r = requests.post(URL, headers = headers, data = data)
    if r.status_code != 200:
        r.raise_for_status()
    return r.text


def getTeams(auth, additionalData, date = None):
    teams = json.loads(requestUrl(auth, "https://rankings.v3.activy.pl/api/query/Activy.Contests.Rankings.Contracts.TeamsRanking", additionalData, date))
    sumoTeams = filter(lambda t: "Sumo" in t['TeamName'], teams)
    
    forEachTeam = map(lambda x: "<li style='background-color: %s'>[%d] %s - <b>%d</b></li>" %
      (colorPerTeam(x['TeamName']), x['Score']['PointsPosition'], x['TeamName'], x['Score']['Points']), sumoTeams)

    return "<h2>Teams</h2><ul>" + "".join(forEachTeam) + "</ul>"

def nameWithAmendments(name):
    if name in ["Kasia O.", "Ala", "Grzegorz O"]:
        return name + " 👪"
    else:
        return name

    
def getUsers(auth, additionalData = "", date = None):
    url = "https://rankings.v3.activy.pl/api/query/Activy.Contests.Rankings.Contracts.ScorePlatform.UserQueries.UserPlayersRanking"
    users = json.loads(requestUrl(auth, url, additionalData, date))
    cyclingResults = json.loads(requestUrl(auth, url, additionalData, date, activityType = 0))
    runningResults = json.loads(requestUrl(auth, url, additionalData, date, activityType = 1))
    
    cyclingDistance = dict([(person["Player"]["Id"], "%d 🚴" % round(person["Score"]["Distance"])) for person in cyclingResults])
    runningDistance = dict([(person["Player"]["Id"], "%d 🏃" % round(person["Score"]["Distance"])) for person in runningResults])
    
    cyclingMaxStreak = dict([(person["Player"]["Id"], "%d 🚴" % round(person["Score"]["MaxStreak"])) for person in cyclingResults])
    runningMaxStreak = dict([(person["Player"]["Id"], "%d 🏃" % round(person["Score"]["MaxStreak"])) for person in runningResults])
    
    usersSorted = sorted(users, key = lambda x: int(x["Score"]["PointsPosition"]), reverse = False)
    forEachUser = map(lambda x: "<tr><td>[%d]</td><td>%s</td><td><b>%d</b></td><td>%s km</td><td>%s</td></tr>" % (
        x["Score"]["PointsPosition"], 
        nameWithAmendments(x["Player"]["NickName"]), 
        x["Score"]["Points"],
        " + ".join(map(str, filter(lambda x: x[:2] != "0 ", [result[x["Player"]["Id"]] for result in [cyclingDistance, runningDistance]]))),
        " + ".join(map(str, filter(lambda x: x[:2] != "0 ", [result[x["Player"]["Id"]] for result in [cyclingMaxStreak, runningMaxStreak]]))),
        ),
    usersSorted)
    return "<table class='table table-striped table-sm'>" +\
    "<tr><th>#</th><th>Who</th><th>Points</th><th>Distance</th><th>Max Streak</th></tr>" +\
    "".join(forEachUser) +"</table>" + "\n<!--" + str(cyclingResults) +" -->"

def colorPerTeam(team):
    colors = {"Sumo Logic Warsaw": "#9A9EAB", "Sumo Logicians": "#EC96A4", "Sumo Logic Bikers": "#DFE166"}
    return colors[team]

def lambda_handler(event, context):
    auth = authenticate()
    
    return """
    <html>
      <head>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        <meta charset="UTF-8"/>
      </head>
      <body>
        <div class="row">
         <div class="jumbotron col-xs-6"> <h2>Standings</h2>
          %s
         </div> 
        </div>
        
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>        
      </body>
    </html>
    """ % (
        # getUsers(auth, additionalData = '"EditionId":"ef802327-30ec-451b-bafe-4a5d30f5d3af",'),
           getUsers(auth))


