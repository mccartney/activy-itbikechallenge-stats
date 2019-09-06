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

def requestUrl(auth, URL):
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

    currentDate = datetime.datetime.now().isoformat("T")[:-3]+"Z"
    data =  '{"ContestId":"8aa8ffc2-496f-4b2d-a26b-2042425124b4","Day":"%s","TeamGroupId":"208858d6-b6d7-411e-a289-475c1b026ba7","Type":"0"}' % currentDate
    r = requests.post(URL, headers = headers, data = data)
    if r.status_code != 200:
        r.raise_for_status()
    return r.text


def getTeams(auth):
    teams = json.loads(requestUrl(auth, "https://rankings.v3.activy.pl/api/query/Activy.Contests.Rankings.Contracts.TeamsRanking"))    
    sumoTeams = filter(lambda t: "Sumo" in t['TeamName'], teams)
    
    forEachTeam = map(lambda x: "<li>[%d] %s - <b>%d</b></li>" % (x['Score']['PointsPosition'], x['TeamName'], x['Score']['Points']), sumoTeams)

    return "<h2>Teams</h2><ul>" + "".join(forEachTeam) + "</ul>"
    
def ourIds():
    return ["b7c6d926-fc8c-4042-a7d8-130c433a0dad",    
     "341093cd-2557-4385-b424-a73eda8d44e6",           
     "f8dc551d-3536-44ac-a306-f1e5883a2427",          
     "bd12f760-8164-45f4-a2df-f501899efe4e",          
     "5bd075b5-f5f9-45b6-b017-1dcd3fd50870",       
     
     "28a746b8-2baf-4511-9a41-8fcf8d633cff",       
     "25dade75-91aa-4560-972b-6cdb1dfef56a",        
     "68671bc5-2c45-4b6e-8cb2-b6d3c8916c99",       
     "ac43105c-c0c8-4e24-a4da-91de986d78bd",        
     "d1e209f3-0437-4abb-9156-c66d76d7c50b",      
     
     "310cc307-b71d-4065-90d6-d9c29af7279c",      
     "7aae52db-d9bf-4355-a30f-e8092ca5a69a",      
     "7f10a04e-e0ab-4f3b-92d6-5cd3676c035b",      
     "506cf2f4-0bde-4d12-b68f-8a0b3553b6dd",       
     
     ]

def getUsers(auth):
    users = json.loads(requestUrl(auth, "https://rankings.v3.activy.pl/api/query/Activy.Contests.Rankings.Contracts.UsersQueries.UserPlayersRanking"))    
    ourUsers = filter(lambda u: u["Player"]["Id"] in ourIds(), users)
    ourUsersSorted = sorted(ourUsers, key = lambda x: int(x["Score"]["PointsPosition"]), reverse = False)
    forEachUser = map(lambda x: "<tr><td>[%d]</td><td>%s</td><td><b>%d</b></td><td>(%d bonus rides + %d km)</td></tr>" % (
        x["Score"]["PointsPosition"], 
        x["Player"]["NickName"], 
        x["Score"]["Points"], 
        x["Score"]["BonusRides"], 
        x["Score"]["Distance"]),
    ourUsersSorted)
    return "<h2>Individuals</h2><table>" + "".join(forEachUser) +"</table>"

def lambda_handler(event, context):
    auth = authenticate()
    
    return "<html><head></head><body>%s %s</body></html>" % (getTeams(auth), getUsers(auth))

