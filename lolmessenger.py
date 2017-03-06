# imports 
from flask import Flask, request
import requests
import json
from cassiopeia import riotapi
import sys
import os


'''-----------------
TODO
Make a request once every few weeks to get champ to id mapping
For free champ request, store the result in db
finish the commands by monday
'''


#setup + auth tokens
app = Flask(__name__)
riot_api_key = os.environ['RIOT_API_KEY']
riotapi.set_region("NA")
riotapi.set_api_key(riot_api_key)
page_auth_token = os.environ['PAT']
verify_token = 'my_voice_is_my_password_verify_me'
help_txt = "commands"
free_champs_txt = "free champs this week"
invalid_cmd_error = " Or your command was invalid, type in 'commands' to get a full list of available commands!"
all_champs_url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&api_key=" + riot_api_key
all_champs = requests.get(all_champs_url).json()["data"]
champ_to_id = {}
help_msg = """Supported messages: 
NOTE: The square brackets are required around the fields

* 'free champs this week'

* 'is summoner [summoner_username] in game?'

* 'top champ masteries for [summoner_username]'

* 'summoner [summoner_username] mastery of champion [champion_name]'

* 'is [server_name] server up?'

* 'set region [region]' for player stats in other regions run this first
"""


# ----- HELPER FUNCTIONS ------ #
def get_free_champs():
	print(all_champs)
	free_champs_url = "https://na.api.pvp.net/api/lol/na/v1.2/champion?freeToPlay=true&api_key=" + riot_api_key
	free_champs = requests.get(free_champs_url).json()["champions"]
	#print free_champs
 	lst_free_champs = [champ["id"] for champ in free_champs]
	print(lst_free_champs)
	lst_names = [all_champs[str(champ_id)]["name"] for champ_id in lst_free_champs]
	print(lst_names)
	return lst_names


#Three can be abstracted to one function
def get_username(msg):
	# make a list of common terms to remove/replace and iterate trought it
	name = msg.lower()
	index1 = name.index("[")
	index2 = name.index("]")
	name = name[index1+1:index2]
	return name

def get_champion_name(msg):
	champ = msg.lower()
	start_index = champ.index("champion")
	index1 = champ.index("[", start_index)
	index2 = champ.index("]", start_index)
	champ = champ[index1+1:index2]
	return champ


def get_server(msg):
	server = msg.lower()
	index1 = server.index("[")
	index2 = server.index("]")
	server = server[index1+1:index2]
	return server

def get_server_status():
	servs = json.loads(riotapi.get_shard().to_json())
	print(servs)
	status = []
	for service in servs["services"]:
		status.append("\n" + service["name"]+ " - " + service["status"] + "\n")
		if len(service["incidents"]) != 0:
			for update in service["incidents"]:
				status.append("\t * " + update["updates"][0]["content"] + "\n")

	#status = [service["name"]+": "+service["status"]+"\n" for service in servs["services"]]
	return status

@app.route('/webhook', methods=['GET'])
#Authenticate for Messenger
def auth():
	req = request.args
	if req.get('hub.verify_token') == verify_token:
		print("Verify token matches")
		return req.get('hub.challenge')
	else:
		print("Invalid token")
		return "Page Not Verified, Invalid verify token"


@app.route('/webhook', methods=['POST'])
#Messages and how to respond to them
# 'help' will show certain structured messages

def send_reply():
	#reply = "Hello World"
	req = request.json["entry"][0]['messaging'][0]
	print(req)

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
		print("U: " + username)
		try:
			user = riotapi.get_summoner_by_name(username)
		except:
			reply = "This player doesn't exist in this region!" + invalid_cmd_error
		else:		
			curr_game = riotapi.get_current_game(user)
			if curr_game is None:
				reply = "They aren't in a game right now!"
			else:
				reply = "Yes! They are in a game :)"

	elif "server up?" in msg_lower:
		server = get_server(sender_msg)
		try:
			riotapi.set_region(server)
		except:
			reply = "Invalid Region!" + invalid_cmd_error
		else:
			serv_status = get_server_status()
			reply = "".join(serv_status)
		finally:
			riotapi.set_region("NA")

	elif "top champ masteries" in msg_lower:
		username = get_username(sender_msg)
		summoner = riotapi.get_summoner_by_name(username)
		print("Username for masteries: " + username)
		reply = ""
		try:
			masteries = riotapi.get_top_champion_masteries(summoner)
			for c in masteries:
				champ = json.loads(c.to_json())
				champ_id = str(champ['championId'])
				print("champ_id: " + champ_id)
				champ_name = all_champs[champ_id]['name']
				reply += champ_name + "\n" 
				champ_level = str(champ['championLevel'])
				reply += "- Level: " +  champ_level + "\n"
				champ_points = str(champ['championPoints'])
				reply += "- Total Points: " +  champ_points + "\n"
				print("champ_name: " + champ_name)
			total_mastery_score = riotapi.get_champion_mastery_score(summoner)
		except:
			reply = "This player doesn't exist in this region!" + invalid_cmd_error
		else:		
			reply += "Total Mastery Score: " +  str(total_mastery_score)
			print("Total Mastery Score: " +  str(total_mastery_score))
			
	elif "mastery of champion" in msg_lower:
		username = get_username(sender_msg)
		summoner = riotapi.get_summoner_by_name(username)
		champ_name = get_champion_name(sender_msg)
		champion = riotapi.get_champion_by_name(champ_name)
		print("User: " + username)
		print("Champ: " + champ_name)
		try:
			print("getting champ_mastery")
			champ_mastery = riotapi.get_champion_mastery(summoner, champion)
			print("to json")
		except:
			reply = "Invalid username/champion!" + invalid_cmd_error
		else:	
			reply = "Mastery here"
			print(champ_mastery)


	elif "set region" in msg_lower:
		region = msg.lower()
		index1 = region.index("[")
		index2 = region.index("]")
		region = region[index1+1:index2]
		try:
			riotapi.set_region(region)
		except:
			reply = "Invalid Region!" + invalid_cmd_error
		else:
			reply = "Region set to " + region

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
