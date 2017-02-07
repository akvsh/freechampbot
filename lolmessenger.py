# imports 
from flask import Flask, request
import requests
import json
from cassiopeia import riotapi
import sys
import os


'''-----------------
TODO
Store in DB (or in a file) mapping between all champs and their id so its faster to access
Cache all the requeses using memecaches for a day
'''


#setup + auth tokens
app = Flask(__name__)
#app.config.from_pyfile('config.py')
#NA only 
riot_api_key = os.environ['RIOT_API_KEY']
riotapi.set_region("NA")
riotapi.set_api_key(riot_api_key)
page_auth_token = os.environ['PAT']
verify_token = 'my_voice_is_my_password_verify_me'
help_txt = "commands"
free_champs_txt = "free champs this week"
help_msg = """Supported messages: 

* 'free champs this week' - get current free champ rotation

* 'is summoner [summoner_username] in game' see if given username is in a game

* 'champ info about [champ]' for details about given champ

* 'summoner stats for [summoner_username]' get some stats for given summoner

* 'is [server_name] server up?' check if NA/EU/etc is up

* 'set region [region]' if you're looking for players/stats in another region
"""


# ----- HELPER FUNCTIONS ------ #
def get_free_champs():
	free_champs_url = "https://na.api.pvp.net/api/lol/na/v1.2/champion?freeToPlay=true&api_key=" + riot_api_key
	free_champs = requests.get(free_champs_url).json()["champions"]
	#print free_champs
 	lst_free_champs = [champ["id"] for champ in free_champs]
	print lst_free_champs
	all_champs_url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&api_key=" + riot_api_key
	all_champs = requests.get(all_champs_url).json()["data"]
	lst_names = [all_champs[str(champ_id)]["name"] for champ_id in lst_free_champs]
	print lst_names
	return lst_names

def get_username(msg):
	name = msg.replace("is summoner", "")
	name = name.replace("in game", "")
	name = name.strip()
	return name

def get_server(msg):
	server = msg.replace("server up?","")
	server = server.replace("is","")
	server = server.strip()
	server = server.upper()
	return server

def get_server_status():
	servs = json.loads(riotapi.get_shard().to_json())
	print servs
	status = []
	status = [service["name"]+":"+service["status"]+"\n" for service in servs["services"]]
	return status

@app.route('/webhook', methods=['GET'])
#Authenticate for Messenger
def auth():
	req = request.args
	if req.get('hub.verify_token') == verify_token:
		print "Verify token matches"
		return req.get('hub.challenge')
	else:
		print "Invalid token"
		return "Page Not Verified, Invalid verify token"


@app.route('/webhook', methods=['POST'])
#Messages and how to respond to them
# 'help' will show certain structured messages

def send_reply():
	#reply = "Hello World"
	req = request.json["entry"][0]['messaging'][0]
	print req

	sender_id = req['sender']['id']
	sender_msg = req['message']['text']
	msg_lower = sender_msg.lower()

	if msg_lower == help_txt:
		reply = help_msg

	elif msg_lower == free_champs_txt:
		#call riot api to get list of free champs
		free_champs = get_free_champs()
		reply = "Free champs for this week: \n" + "".join("- "+champ+"\n" for champ in free_champs)

	elif "is summoner" in msg_lower and "in game" in msg_lower:
		username = get_username(sender_msg)
		user = riotapi.get_summoner_by_name(username)
		curr_game = riotapi.get_current_game(user)
		if curr_game is None:
			reply = "They aren't in a game right now!"
		else:
			reply = "Yes! They are in a game :)"

	elif "server up?" in msg_lower:
		server = get_server(sender_msg)
		riotapi.set_region(server)
		serv_status = get_server_status()
		riotapi.set_region("NA")
		reply = "".join(serv_status)

	else:
		reply = sender_msg
	
	headers = {
		'Content-Type': 'application/json'
	}
	params = {
		'access_token': page_auth_token
	}
	resp = {
		'recipient': {
			'id': sender_id
		},
		'message': {
			'text': reply
		}
	}
	r = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, json=resp, headers=headers)
	sys.stdout.flush()
	return "Reply Sent"

'''

#helper functions
def is_in_game(summoner_name):
	#check if summoner_name is playing right now


#not a priority, get above two working first
def champ_mastery(summoner_name, champ=None):
	#top 3 champ masteries of summoner_name (Default)
	#Champ mastery of 'champ' (second arg)
	if champ == None:
		#default
	else:

'''


if __name__ == "__main__":
	app.run()
