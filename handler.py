import json
from botocore.vendored import requests
import datetime

def authenticate():
   URL='https://players.v3.activy.pl/auth/connect/token' 
   headers = {
         'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0' ,
         'Accept': '*/*', 
         'Accept-Language': 'en-GB,en;q=0.7,en-US;q=0.3' ,
         'Referer': 'https://stats.activy.pl/teams', 
         'Authorization': 'Basic REDACTED' ,
         'Content-Type': 'application/x-www-form-urlencoded', 
         'Origin': 'https://stats.activy.pl', 
         'DNT': '1', 
         'TE': 'Trailers'
   }
   data = 'grant_type=password&scope=openid+email+offline_access+activy.players+activy.contests+activy.rides&username=REDACTED&password=REDACTED'
   r = requests.post(URL, headers = headers, data = data)
   access_token = json.loads(r.text)["access_token"]
   return access_token

def requestUrl(auth, URL, additionalData, date = None):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.7,en-US;q=0.3',
        'Referer': 'https://stats.activy.pl/teams',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth,
        'Origin': 'https://stats.activy.pl', 
        'DNT': '1',
        'Connection': 'keep-alive',
        'TE': 'Trailers' 
    }    
 
    if not date: 
        date = datetime.datetime.now().isoformat("T")[:-3]+"Z"
        
    data =  '{%s"ContestId":"8aa8ffc2-496f-4b2d-a26b-2042425124b4","Day":"%s","TeamGroupId":"208858d6-b6d7-411e-a289-475c1b026ba7","Type":"0"}' % (additionalData,date)
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
    
def ourIds():
    return {
     "b7c6d926-fc8c-4042-a7d8-130c433a0dad": "Sumo Logic Warsaw",
     "341093cd-2557-4385-b424-a73eda8d44e6": "Sumo Logic Warsaw",
     "f8dc551d-3536-44ac-a306-f1e5883a2427": "Sumo Logic Warsaw",
     "bd12f760-8164-45f4-a2df-f501899efe4e": "Sumo Logic Warsaw",
     "5bd075b5-f5f9-45b6-b017-1dcd3fd50870": "Sumo Logic Warsaw",
     
     "28a746b8-2baf-4511-9a41-8fcf8d633cff": "Sumo Logicians",
     "25dade75-91aa-4560-972b-6cdb1dfef56a": "Sumo Logicians",
     "68671bc5-2c45-4b6e-8cb2-b6d3c8916c99": "Sumo Logicians",
     "ac43105c-c0c8-4e24-a4da-91de986d78bd": "Sumo Logicians",
     "d1e209f3-0437-4abb-9156-c66d76d7c50b": "Sumo Logicians",
     
     "310cc307-b71d-4065-90d6-d9c29af7279c": "Sumo Logic Bikers",
     "7aae52db-d9bf-4355-a30f-e8092ca5a69a": "Sumo Logic Bikers",
     "7f10a04e-e0ab-4f3b-92d6-5cd3676c035b": "Sumo Logic Bikers",
     "506cf2f4-0bde-4d12-b68f-8a0b3553b6dd": "Sumo Logic Bikers",
     "4f6aaac9-6cd8-40c6-a783-6db09b1eed15": "Sumo Logic Bikers",
    }     

def getUsers(auth, additionalData, date = None):
    users = json.loads(requestUrl(auth, "https://rankings.v3.activy.pl/api/query/Activy.Contests.Rankings.Contracts.UsersQueries.UserPlayersRanking", additionalData, date))
    ourUsers = filter(lambda u: u["Player"]["Id"] in ourIds().keys(), users)
    ourUsersSorted = sorted(ourUsers, key = lambda x: int(x["Score"]["PointsPosition"]), reverse = False)
    forEachUser = map(lambda x: "<tr style='background-color:%s'><td>[%d]</td><td>%s</td><td><b>%d</b></td><td>(%d bonus rides + %d km)</td></tr>" % (
        colorPerTeam(ourIds()[x["Player"]["Id"]]),
        x["Score"]["PointsPosition"], 
        x["Player"]["NickName"], 
        x["Score"]["Points"], 
        x["Score"]["BonusRides"], 
        x["Score"]["Distance"]),
    ourUsersSorted)
    return "<h2>Individuals</h2><table>" + "".join(forEachUser) +"</table>"

def colorPerTeam(team):
    colors = {"Sumo Logic Warsaw": "#9A9EAB", "Sumo Logicians": "#EC96A4", "Sumo Logic Bikers": "#DFE166"}
    return colors[team]

def lambda_handler(event, context):
    auth = authenticate()
    
    edition4 = """"EditionId": "9b35cec2-fc21-4553-9703-e7f9bc5486d8", """

    edition3 = """"EditionId": "6c799830-0b49-496c-bd59-c86d6beaad01","""
    edition3End = "2019-10-06T21:59:59.000Z"

    return """
    <html>
      <head>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
      </head>
      <body>
        <div class="row">
         <div class="jumbotron col-xs-6 bg-success"> <h2>Edition 4</h2>
          %s %s
         </div> 
         <div class="jumbotron col-xs-6"> <h2>Edition 3</h2>
          %s %s
         </div> 
         <div class="jumbotron col-xs-6"><h2>Overall</h2>
          %s %s
         </div> 
        </div>
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>        
      </body>
    </html>
    """ % (
           getTeams(auth, edition4), getUsers(auth, edition4),
           getTeams(auth, edition3, edition3End), getUsers(auth, edition3, edition3End),
           getTeams(auth, ""), getUsers(auth, ""),
           )


