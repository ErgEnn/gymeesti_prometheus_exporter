from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR
import requests
import argparse

REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(GC_COLLECTOR)

app = Flask(__name__)

gauge = Gauge('people_count', 'Count of people in gym', ['id', 'name'])
token = None
clubs = None

parser = argparse.ArgumentParser()
parser.add_argument('--email', help='email', required=True)
parser.add_argument('--pw', help='password', required=True)
args = parser.parse_args()

def get_token():
    global token, args
    if token is None:
        sign_in_data = {
            'email': args.email,
            'password': args.pw,
            'clientApplicationInfo': {
                'type': 'WhiteLabel',
                'whiteLabelId': '57F56624-35D7-4CD6-9863-24FC974673B8'
            }
        }
        auth_response = requests.post('https://goapi2.perfectgym.com/v1/Authorize/LogInWithEmail', json=sign_in_data)
        token = auth_response.json()['data']['token']
    return token

def get_clubs():
    global clubs
    if clubs is None:
        clubs_response = requests.get('https://goapi2.perfectgym.com/v1/Clubs/Clubs', headers={'Authorization': 'Bearer '+get_token()})
        clubs = {k:v for (k,v) in map(lambda x: (x['id'], x['name']), clubs_response.json()['data'])}
    return clubs

def get_club_name(id):
    _clubs = get_clubs()
    if id in _clubs:
        return _clubs[id]
    global clubs
    clubs = None
    _clubs = get_clubs()
    if id in _clubs:
        return _clubs[id]
    return 'Unknown club '+id

@app.route('/metrics')
def metrics():
    global gauge
    people_count_response = requests.get('https://goapi2.perfectgym.com/v1/Clubs/WhoIsInCount', headers={'Authorization': 'Bearer '+get_token()})

    for data_row in people_count_response.json()['data']:
        gauge.labels(id=data_row['clubId'], name=get_club_name(data_row['clubId'])).set(data_row['count'])

    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
