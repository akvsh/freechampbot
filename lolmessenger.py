# imports 
from flask import Flask, request
import requests
import json
from cassiopeia import riotapi
import sys


'''-----------------
TODO
Store in DB (or in a file) mapping between all champs and their id so its faster to access
Cache all the requeses using memecaches for a day
'''


#setup + auth tokens
app = Flask(__name__)
#app.config.from_pyfile('config.py')
#NA only 
riot_api_key = "40073319-c490-4dca-b8cb-83c24fd00839"
riotapi.set_region("NA")
riotapi.set_api_key(riot_api_key)
page_auth_token = 'EAAaF14INvz4BAPBZAbCZAUOpkDBlHmFxFkYaJPJ83bYeZCwH0kJbe7Ru38IkAJO7P4dFDDKqF4ZBLXb8NV4C1tU461MhSBKoJIdub3Nolrxz11DGuWkpdyGdjlOEBDLIbqqZBeNsvcstCWqtQATSsLyNtKYP8F7e385saBJDulAZDZD'
verify_token = 'my_voice_is_my_password_verify_me'
help_txt = "commands"
help_msg = """Supported messages: 

* 'free champs this week' - get current free champ rotation

* 'is summoner [summoner_username] on' see if given username is online

* 'champ info about [champ]' for details about given champ

* '[item_name] item info for [item_name]' for details about given item

* 'summoner stats for [summoner_username]' get some stats for given summoner

* 'is [server_name] server up?' check if NA/EU/etc is up
"""


# ----- HELPER FUNCTIONS ------ #
def get_free_champs():
	free_champs_url = "https://na.api.pvp.net/api/lol/na/v1.2/champion?freeToPlay=true&api_key=" + riot_api_key
	free_champs = requests.get(free_champs_url)
	print free_champs
 	#lst_free_champs = [champ["id"] for champ in free_champs["champs"]]
	#print lst_free_champs
	all_champs_url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&api_key=" + riot_api_key
	all_champs = requests.get(all_champs_url)
	print all_champs
	#lst_names = [all_champs["data"][champ_id]["name"] for champ_id in lst_free_champs]
	#return free_champs



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
	elif msg_lower == "free champs this week":
		#call riot api to get list of free champs
		get_free_champs()
		reply = "free champs here"
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
def free_champs():
	#will call riot api and return the free week champs


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
